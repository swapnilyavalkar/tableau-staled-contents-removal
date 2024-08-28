SELECT DISTINCT _sites.name AS "SITE_NAME", workbooks.id AS "WORKBOOK_ID", _Workbooks.owner_name AS "OWNER_NAME", _Workbooks.project_name AS "PROJECT_NAME", _Workbooks.name AS "WORKBOOK_NAME", workbooks.luid AS "WORKBOOK_LUID", MAX(_views_stats.last_view_time) AS "LAST_VIEWED_DATE", DATE_PART('day',CURRENT_DATE - MAX(_views_stats.last_view_time)) AS "NOT_USED_SINCE_DAYS", _sites.url_namespace AS "SITE_URL_NAMESPACE", CASE WHEN _sites.name LIKE 'Default' THEN CONCAT('https://abc.com', '/#/workbooks/', workbooks.id, '/views/') ELSE CONCAT('https://abc.com', '/#/site/', _sites.url_namespace, '/workbooks/', workbooks.id, '/views/') END AS "WORKBOOK_URL" FROM _Workbooks INNER JOIN _Views ON _Workbooks.id = _Views.workbook_id LEFT JOIN _Subscriptions ON Case WHEN _Subscriptions.workbook_url IS NULL THEN _Subscriptions.view_url else _Subscriptions.workbook_url END = Case WHEN _Subscriptions.workbook_url IS NULL then _Views.view_url ELSE _Workbooks.workbook_url END INNER JOIN workbooks ON Workbooks.id =_Workbooks.id LEFT JOIN _views_stats ON _views.id = _views_stats.views_id LEFT JOIN _sites ON _views_stats.site_id = _sites.id WHERE _Subscriptions.id is null AND _sites.name NOT IN ('Default') AND _Workbooks.project_name NOT LIKE '%abc%' AND _Workbooks.project_name NOT LIKE '%abc%' AND _Workbooks.project_name NOT LIKE '%xyz%' AND _Workbooks.name NOT LIKE '%abc%' AND _Workbooks.name NOT LIKE '%abc%' AND _Workbooks.name NOT LIKE '%xyz%' GROUP BY _Workbooks.owner_name , _Workbooks.project_name , _Workbooks.name , workbooks.luid, workbooks.id, _sites.name, _sites.url_namespace