curl 'http://localhost:5000/api/v1/topics/test/predict' \
-X POST \
-H "Content-Type:application/json" \
-d '{
    "dataset": [
        {
            "sentence": "A, B, C",
            "likes": 34,
            "sentiment_percentage": 12.32,
            "post_id": 1233,
            "posted_by": 1,
            "parent_tag": "Neutral"
        },
        {
            "sentence": "Databaza",
            "likes": 34,
            "sentiment_percentage": 12.32,
            "post_id": 1233,
            "posted_by": 1,
            "parent_tag": "Neutral"
        }
    ]
}'