# 解題思路
## 1. 先將兩表格進行合併(依據product及memberid作為合併的依據)，合併方式使用LEFT JOIN以Notification表作為主體，因為是要看推波有沒有效果
## 2. 因為要計算轉換率，需要「可歸因購買」，依據其定義：點擊推波30分鐘內完成購買，所以使用timestampdiff函數來計算Notification及Purchase的時間差
## 3. 將此時間差用CASE WHEN判斷，符合30分鐘內的計為1不符合則為0，設定為Behavior_Could_Detect欄位
## 4. 合併完成後再進行WHERE篩選將product為X的資料篩選出來
## 5. 以上1-4的結果用CTE命名為A
## 6. 將A中Behavior_Could_Detect欄位進行加總，得出的結果是A商品的可歸因購買，將A的資料進行COUNT則是算出A商品的總推播次數，兩者相除及可計算出商品X的轉換率
WITH A AS (
    SELECT NC.event AS NC_E,
           NC.product AS NC_P,
           NC.memberId AS NC_Id,
           NC.createdAt AS NC_CT,
           EC.event AS EC_E,
           EC.product AS EC_P,
           EC.memberId AS EC_Id,
           EC.createdAt AS EC_CT,
           timestampdiff(minute,NC.createdAt,EC.createdAt) AS DateDiff,
           CASE WHEN timestampdiff(minute,NC.createdAt,EC.createdAt) <= 30 THEN 1
                WHEN timestampdiff(minute,NC.createdAt,EC.createdAt) > 30 THEN 0
                END AS Behavior_Could_Detect
           FROM notification_clicked AS NC
        LEFT JOIN ec_purchased AS EC
        ON NC.product = EC.product AND NC.memberId = EC.memberId
        WHERE NC.product = 'X'
)

SELECT SUM(Behavior_Could_Detect)/COUNT(*) AS Conversion_Rate FROM A;

