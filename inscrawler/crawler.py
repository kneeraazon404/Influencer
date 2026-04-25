import glob
import json
import os
import re
import sys
import time
import traceback
from time import sleep

from selenium.webdriver.common.by import By
from tqdm import tqdm

from inscrawler import secret
from inscrawler.browser import Browser
from inscrawler.exceptions import RetryException
from inscrawler.fetch import (
    fetch_caption,
    fetch_comments,
    fetch_datetime,
    fetch_details,
    fetch_imgs,
    fetch_likers,
    fetch_likes_plays,
)
from inscrawler.utils import instagram_int, randmized_sleep, retry


class Logging:
    PREFIX = "instagram-crawler"

    def __init__(self):
        try:
            timestamp = int(time.time())
            self.cleanup(timestamp)
            self.logger = open("/tmp/%s-%s.log" % (Logging.PREFIX, timestamp), "w")
            self.log_disable = False
        except Exception:
            self.log_disable = True

    def cleanup(self, timestamp):
        days = 86400 * 7
        days_ago_log = "/tmp/%s-%s.log" % (Logging.PREFIX, timestamp - days)
        for log in glob.glob("/tmp/instagram-crawler-*.log"):
            if log < days_ago_log:
                os.remove(log)

    def log(self, msg):
        if self.log_disable:
            return
        self.logger.write(msg + "\n")
        self.logger.flush()

    def __del__(self):
        if self.log_disable:
            return
        self.logger.close()


class InsCrawler(Logging):
    URL = "https://www.instagram.com"
    RETRY_LIMIT = 10

    def __init__(self, has_screen=False):
        super().__init__()
        self.browser = Browser(has_screen)
        self.page_height = 0
        self.login()

    def _dismiss_login_prompt(self):
        ele_login = self.browser.find_one(".Ls00D .Szr5J")
        if ele_login:
            ele_login.click()

    def login(self):
        browser = self.browser
        url = "%s/accounts/login/" % InsCrawler.URL
        browser.get(url)
        sleep(2)

        try:
            buttons = browser.driver.find_elements(
                By.XPATH,
                "//button[contains(text(), 'Allow') or contains(text(), 'Accept')]",
            )
            for btn in buttons:
                if btn.is_displayed():
                    btn.click()
                    sleep(2)
                    break
        except Exception:
            pass

        try:
            u_input = browser.find_one('input[name="username"]', waittime=10)
            u_input.send_keys(secret.username)
            p_input = browser.find_one('input[name="password"]', waittime=10)
            p_input.send_keys(secret.password)
        except Exception:
            print("Error: Could not find login fields. This might be due to:")
            print("1. Network slowness or timeouts.")
            print("2. Instagram detecting automation (headless mode).")
            print("3. Captcha or unusual login flow.")
            print("4. Empty or invalid credentials in inscrawler/secret.py")
            raise

        login_btn = browser.find_one(".L3NKy")
        if login_btn:
            login_btn.click()
        else:
            submit = browser.find_one('button[type="submit"]')
            if submit:
                submit.click()

        @retry()
        def check_login():
            if browser.find_one('input[name="username"]'):
                raise RetryException()

        check_login()

    def get_user_profile(self, username):
        browser = self.browser
        url = "%s/%s/" % (InsCrawler.URL, username)
        browser.get(url)
        name = browser.find_one(".rhpdm")
        desc = browser.find_one(".-vDIg span")
        photo = browser.find_one("._6q-tv")
        statistics = [ele.text for ele in (browser.find(".g47SY") or [])]
        post_num, follower_num, following_num = statistics if len(statistics) == 3 else ("", "", "")
        return {
            "name": name.text if name else "",
            "desc": desc.text if desc else None,
            "photo_url": photo.get_attribute("src") if photo else None,
            "post_num": post_num,
            "follower_num": follower_num,
            "following_num": following_num,
        }

    def get_user_profile_from_script_shared_data(self, username):
        browser = self.browser
        url = "%s/%s/" % (InsCrawler.URL, username)
        browser.get(url)
        source = browser.driver.page_source
        p = re.compile(r"window._sharedData = (?P<json>.*?);</script>", re.DOTALL)
        match = re.search(p, source)
        if not match:
            raise ValueError("Could not find _sharedData on profile page")
        data = json.loads(match.group("json"))
        user_data = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]
        return {
            "name": user_data["full_name"],
            "desc": user_data["biography"],
            "photo_url": user_data["profile_pic_url_hd"],
            "post_num": user_data["edge_owner_to_timeline_media"]["count"],
            "follower_num": user_data["edge_followed_by"]["count"],
            "following_num": user_data["edge_follow"]["count"],
            "website": user_data["external_url"],
        }

    def get_user_posts(self, username, number=None, detail=False):
        user_profile = self.get_user_profile(username)
        if not number:
            number = instagram_int(user_profile["post_num"])

        self._dismiss_login_prompt()

        if detail:
            return self._get_posts_full(number)
        else:
            return self._get_posts(number)

    def get_latest_posts_by_tag(self, tag, num):
        url = "%s/explore/tags/%s/" % (InsCrawler.URL, tag)
        self.browser.get(url)
        return self._get_posts(num)

    def auto_like(self, tag="", maximum=1000):
        browser = self.browser
        if tag:
            url = "%s/explore/tags/%s/" % (InsCrawler.URL, tag)
        else:
            url = "%s/explore/" % InsCrawler.URL
        self.browser.get(url)

        ele_post = browser.find_one(".v1Nh3 a")
        if not ele_post:
            print("Could not find posts to like.")
            return
        ele_post.click()

        for _ in range(maximum):
            heart = browser.find_one(".dCJp8 .glyphsSpriteHeart__outline__24__grey_9")
            if heart:
                heart.click()
                randmized_sleep(2)

            left_arrow = browser.find_one(".HBoOv")
            if left_arrow:
                left_arrow.click()
                randmized_sleep(2)
            else:
                break

    def _get_posts_full(self, num):
        @retry()
        def check_next_post(cur_key):
            ele_a_datetime = browser.find_one(".eo2As .c-Yi7")
            if ele_a_datetime is None:
                raise RetryException()
            next_key = ele_a_datetime.get_attribute("href")
            if cur_key == next_key:
                raise RetryException()

        browser = self.browser
        browser.implicitly_wait(1)
        browser.scroll_down()
        ele_post = browser.find_one(".v1Nh3 a")
        ele_post.click()
        dict_posts = {}

        pbar = tqdm(total=num)
        pbar.set_description("fetching")
        cur_key = None

        all_posts = self._get_posts(num)
        i = 1

        for _ in range(num):
            dict_post = {}
            try:
                if i < num:
                    check_next_post(all_posts[i]["key"])
                    i += 1

                ele_a_datetime = browser.find_one(".eo2As .c-Yi7")
                cur_key = ele_a_datetime.get_attribute("href")
                dict_post["key"] = cur_key
                fetch_datetime(browser, dict_post)
                fetch_imgs(browser, dict_post)
                fetch_likes_plays(browser, dict_post)
                fetch_likers(browser, dict_post)
                fetch_caption(browser, dict_post)
                fetch_comments(browser, dict_post)

            except RetryException:
                sys.stderr.write(
                    "\x1b[1;31m"
                    + "Failed to fetch the post: "
                    + (cur_key or "URL not fetched")
                    + "\x1b[0m\n"
                )
                break

            except Exception:
                sys.stderr.write(
                    "\x1b[1;31m"
                    + "Failed to fetch the post: "
                    + (cur_key if isinstance(cur_key, str) else "URL not fetched")
                    + "\x1b[0m\n"
                )
                traceback.print_exc()

            self.log(json.dumps(dict_post, ensure_ascii=False))
            dict_posts[browser.current_url] = dict_post
            pbar.update(1)

        pbar.close()
        posts = list(dict_posts.values())
        if posts:
            posts.sort(key=lambda post: post.get("datetime", ""), reverse=True)
        return posts

    def _get_posts(self, num):
        TIMEOUT = 600
        browser = self.browser
        key_set = set()
        posts = []
        pre_post_num = 0
        wait_time = 1

        pbar = tqdm(total=num)

        def start_fetching(pre_post_num, wait_time):
            ele_posts = browser.find(".v1Nh3 a") or []
            for ele in ele_posts:
                key = ele.get_attribute("href")
                if key not in key_set:
                    dict_post = {"key": key}
                    ele_img = browser.find_one(".KL4Bh img", ele)
                    if ele_img:
                        dict_post["caption"] = ele_img.get_attribute("alt")
                        dict_post["img_url"] = ele_img.get_attribute("src")

                    fetch_details(browser, dict_post)

                    key_set.add(key)
                    posts.append(dict_post)

                    if len(posts) == num:
                        break

            if pre_post_num == len(posts):
                pbar.set_description("Wait for %s sec" % wait_time)
                sleep(wait_time)
                pbar.set_description("fetching")
                wait_time *= 2
                browser.scroll_up(300)
            else:
                wait_time = 1

            pre_post_num = len(posts)
            browser.scroll_down()
            return pre_post_num, wait_time

        pbar.set_description("fetching")
        while len(posts) < num and wait_time < TIMEOUT:
            post_num, wait_time = start_fetching(pre_post_num, wait_time)
            pbar.update(post_num - pre_post_num)
            pre_post_num = post_num

            loading = browser.find_one(".W1Bne")
            if not loading and wait_time > TIMEOUT / 2:
                break

        pbar.close()
        print("Done. Fetched %s posts." % min(len(posts), num))
        return posts[:num]
