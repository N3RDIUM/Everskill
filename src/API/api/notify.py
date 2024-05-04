from pywebpush import webpush, WebPushException

try:
    webpush(
        subscription_info={
            "endpoint": "https://updates.push.services.mozilla.com/wpush/v2/gAAAAABmNLqNfthc9m1jlyKneK9Ly_MnVedlYWy3Z7-q4oy0a2Bzn7Zu5Mbj_10oUKvX_ZzrtxIVHZfcIzGYX2FeaTihgx7CSAPTsnchP2AZw4NRvR5yrBUTi33i0w6Jmcu0qDBucpJl52wmAvrQXLORjhv16i1acqztYHo3K4rBpY-8IkoGTGU",
            "keys": {
                "p256dh": "BJBMHFzQBKbjbd4eTpGXvTCe7r1gLcpOVYffWIq8ADEY9nQBvXdpmXKDrVBKR-76eUOVygw42757kQaHQ4-gan8",
                "auth": "vCusazBiadImSTUjxwxGTg"
            }
        },
        data="PuSH NotIfSICAS aRe wORiskifnf!",
        vapid_private_key="eJ3w-31S1XcOhnCgKBTbbLwzyCdv4s3RCVXhmSqOdwY",
        vapid_claims={"sub": "mailto:n3rdium@gmail.com"}
    )
except WebPushException as ex:
    print("I'm sorry, Dave, but I can't do that: {}", repr(ex))
    # Mozilla returns additional information in the body of the response.
    if ex.response and ex.response.json():
        extra = ex.response.json()
        print("Remote service replied with a {}:{}, {}",
              extra.code,
              extra.errno,
              extra.message
        )
