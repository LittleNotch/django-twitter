from notifications.models import Notification
from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'
NOTIFICATION_URL = '/api/notifications/'


class NotificationTests(TestCase):

    def setUp(self):
        self.linghu, self.linghu_client = self.create_user_and_client('linghu')
        self.dongxie, self.dongxie_client = self.create_user_and_client('dongxie')
        self.dongxie_tweet = self.create_tweet(self.dongxie)

    def test_comment_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.linghu_client.post(COMMENT_URL, {
            'tweet_id': self.dongxie_tweet.id,
            'content': 'test',
        })
        self.assertEqual(Notification.objects.count(), 1)

    def test_like_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.linghu_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.dongxie_tweet.id,
        })
        self.assertEqual(Notification.objects.count(), 1)


class NotificationApiTests(TestCase):

    def setUp(self):
        self.linghu, self.linghu_client = self.create_user_and_client('linghu')
        self.dongxie, self.dongxie_cliet = self.create_user_and_client('dongxie')
        self.linghu_tweet = self.create_tweet(self.linghu)

    def test_unread_count(self):
        self.dongxie_cliet.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.linghu_tweet.id,
        })

        url = '/api/notifications/unread-count/'
        response = self.linghu_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 1)

        comment = self.create_comment(self.linghu, self.linghu_tweet)
        self.dongxie_cliet.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        response = self.linghu_client.get(url)
        self.assertEqual(response.data['unread_count'], 2)

    def test_mark_all_as_read(self):
        self.dongxie_cliet.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.linghu_tweet.id,
        })
        comment = self.create_comment(self.linghu, self.linghu_tweet)
        self.dongxie_cliet.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id
        })

        unread_url = '/api/notifications/unread-count/'
        response = self.linghu_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        mark_url = '/api/notifications/mark-all-as-read/'
        response = self.linghu_client.get(mark_url)
        self.assertEqual(response.status_code, 405)
        response = self.linghu_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 2)
        response = self.linghu_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_list(self):
        self.dongxie_cliet.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.linghu_tweet.id,
        })
        comment = self.create_comment(self.linghu, self.linghu_tweet)
        self.dongxie_cliet.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        # anonymous cannot access api
        response = self.anonymous_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 403)

        # dongxie cannot see any notification
        response = self.dongxie_cliet.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

        # linghu can see 2 notifications
        response = self.linghu_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

        # see 1 notification after marked
        notification = self.linghu.notifications.first()
        notification.unread = False
        notification.save()
        response = self.linghu_client.get(NOTIFICATION_URL)
        self.assertEqual(response.data['count'], 2)
        response = self.linghu_client.get(NOTIFICATION_URL, {'unread': True})
        self.assertEqual(response.data['count'], 1)
        response = self.linghu_client.get(NOTIFICATION_URL, {'unread': False})
        self.assertEqual(response.data['count'], 1)


    def test_update(self):
        self.dongxie_cliet.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.linghu_tweet.id,
        })
        comment = self.create_comment(self.linghu, self.linghu_tweet)
        self.dongxie_cliet.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        notification = self.linghu.notifications.first()

        url = '/api/notifications/{}/'.format(notification.id)

        # post not allowed, use put
        response = self.dongxie_cliet.post(url, {'unread': False})
        self.assertEqual(response.status_code, 405)

        # others cannot change notification status
        response = self.anonymous_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 403)

        # queryset is based on current logged in user, return 404 instead of 403
        response = self.dongxie_cliet.put(url, {'unread': False})
        self.assertEqual(response.status_code, 404)

        # success case marked as read
        response = self.linghu_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 200)
        unread_url = '/api/notifications/unread-count/'
        response = self.linghu_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 1)

        # mark as unread again
        response = self.linghu_client.put(url, {'unread': True})
        response = self.linghu_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        # must take unread
        response = self.linghu_client.put(url, {'verb': 'newverb'})
        self.assertEqual(response.status_code, 400)

        # cannot change other info
        response = self.linghu_client.put(url, {'verb': 'newverb', 'unread': False})
        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertNotEqual(notification.verb, 'newverb')





