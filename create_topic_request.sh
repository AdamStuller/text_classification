curl http://0.0.0.0:5000/api/v1/topics -X POST \
-F 'description=Topic for banks comment classification' \
-F 'mailto=adam.syn007@gmail.com' \
-F 'dataset=@/Users/adamstuller/Desktop/temp.csv'  \
-F 'name=banks'  \
