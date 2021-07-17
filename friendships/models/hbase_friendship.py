from django_hbase import models


class HBaseFollowing(models.HBaseModel):
    """
    from_user_id follows a list of people, row_key is from_user_id + created_at sorted
    can support
        - A follow all the people (by created_at)
        - time range [] A follow who
        - time spot before/after A follow who
    """
    # row key
    from_user_id = models.IntegerField(reverse=True)
    created_at = models.TimestampField()
    # column key
    to_user_id = models.IntegerField(column_family='cf')

    class Meta:
        table_name = 'twitter_followings'
        row_key = ('from_user_id', 'created_at')

class HBaseFollower(models.HBaseModel):
    """
    who follow to_user_id, row key is to_user_id + created_at sorted
    can support
        - A followers (by created_at)
        - time range[] who follow A
        - time spot before/after who follow A
    """
    # row key
    to_user_id = models.IntegerField(reverse=True)
    created_at = models.TimestampField()
    # column key
    from_user_id = models.IntegerField(column_family='cf')

    class Meta:
        row_key = ('to_user_id', 'created_at')
        table_name = 'twitter_followers'