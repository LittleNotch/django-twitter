from likes.models import Like
from likes.tasks import async_create_like_main_task
from testing.testcases import TestCase


class LikeTaskTests(TestCase):

    def setUp(self):
        super(LikeTaskTests, self).setUp()
        self.linghu = self.create_user('linghu')
        self.dongxie = self.create_user('dongxie')

    def test_async_create_like_main_task(self):
        # test like a tweet
        tweet = self.create_tweet(self.linghu)
        self.create_like(self.linghu, tweet)

        # Tweet content_type_int 1
        content_type = 1
        msg = async_create_like_main_task(content_type, tweet.id, self.linghu.id)
        self.assertEqual(msg, '1 like created.')
        self.assertEqual(1, Like.objects.count())

        # test like a comment
        comment = self.create_comment(self.dongxie, tweet)
        self.create_like(self.linghu, comment)

        # Comment content_type_int 0
        content_type = 0
        msg = async_create_like_main_task(content_type, comment.id, self.linghu.id)
        self.assertEqual(msg, '1 like created.')
        self.assertEqual(2, Like.objects.count())




