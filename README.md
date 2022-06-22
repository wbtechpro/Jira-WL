# Introduction

### The goal of the software is to split transactions in Finolog into projects and orders.

<b>Finolog received a transaction and it is splitted.</b>

1. Finolog sees a transaction — a trigger fires in [Zapier](https://zapier.com/app/editor/108960491)
2. Next, Finolog tries to understand what it is splitting — it looks for the application and its dates.
3. At the moment when a person fills out the [form](http://link.wbtech.pro/report) — the [zap](https://zapier.com/app/editor/115182238) processes his or her data and the embedded [subzap](https://zapier.com/app/editor/123511888) calculates his or her bid for the period specified by the person in the app. In order for the bid to be calculated, the [worklogs site](http://jira-wl.wbtech.pro/jira-client-admin/) must contain the person's logs for the period specified in the application.
4. Then the zap sends [split command](https://zapier.com/app/editor/108960491/nodes/125010111/fields).
5. This command [launches the code](https://zapier.com/app/editor/125009499) which takes data from the server.

<b>Splitting a specific payroll transaction by report date:</b>

1. Executed when we send a command to the Slack channel — [rzbtt/рзбтт transaction id](https://zapier.com/app/editor/123606035/nodes/123606035/fields), which needs to be split (rzbtt/рзбтт 43629927).
2. Zapier receives this command and tries to calculate the dates of the worklog period, which need to be broken down by the accrual date (report_date in Finolog), which is currently manually set by the financial.
3. Next, the zap sends a command to [split](https://zapier.com/app/editor/125009499).
4. This command runs the code that fetches data from the worklogs site.

<b>Splitting for wage-rate employees:</b>

1. Executed when we [send](https://zapier.com/app/editor/151588481/nodes/151589405) to the Slack channel transaction id and list the projects the employee worked on separated by commas (47811615 BLOG-229,BLOG-234,WBT-1355,WBT-1409). 
2. Zapier receives this command and sends a command to [split](https://zapier.com/app/editor/125009499).
3. This command runs the code that fetches data from the worklogs site.


# For users

### Specifying the number of days and the end date of the countdown for loading worklogs

* On the [main page of admin panel](https://jira-wl.wbtech.pro/jira-client-admin/) in the Client app the ["! Period for which worklogs need to be downloaded"/«! Период, за которые необходимо загрузить ворклоги»](https://jira-wl.wbtech.pro/jira-client-admin/client/daysfordownloadmodel/worklogs-download-period/) item was created.

* Clicking on the item opens the page with two input fields.

* The fields display the current number of days for which you need to download worklogs, and the end date of the countdown, both entered through the admin panel.

* <b>Important!</b> If the number of days and/or the end date is manually specified when calling the `run_client` command in the terminal, then they take precedence over the values set via the admin panel.
  
    * Default (applied if otherwise is not specified through the admin panel or when calling the `run_client` command) the end date of the countdown is the current one. 
  
    * Default number of days for which you need to upload worklogs is not set. Without specifying the number of days, loading worklogs will not work — you must either install it through the admin panel, or manually pass the `run_client` django command as an argument.

* If the forms in the admin panel are empty, then at the moment the number of days for uploading worklogs and the end date are not set.

* To set/change the number of days and the end date, enter an integer/date in the appropriate fields and click "Submit".
    * The end date is specified in YYYY-MM-DD format.
  
    * The number of days must not exceed 3 months from the specified date. That is, for example, with an end date of 2022-02-01, worklogs can only be displayed in the time range from 2022-01-31 to 2021-11-01 inclusively.

* The parameters set through the admin panel are saved and are not reset automatically.
  * The set values will remain in effect until they are changed or deleted.

* In the event that it is necessary to delete the value(s), you must enter an empty line in the corresponding field(s) and click "Submit".


### Automatic update of the date and number of days on the 28th of each month

* This functionality is needed in order to monthly upload worklogs from the 28th of the previous month to the 27th of the current month inclusively.

* On the night of the 28th day of each month, there is an automatic update or setting (if the fields were empty before) of the end date and the number of days for loading worklogs:
  * The end date is the current one, that is, the 28th of the current month and year;
  * The number of days is different each time. Depends on how many days there are in the current calendar month (for example, 31 in January, 28 in February).

* After updating the date and the number of days on the night of the 28th, worklogs for the specified period are loaded.


### Automatic date update on every Tuesday

* This functionality is needed so that worklogs for the previous period are loaded every Tuesday.

* The command does not work if Tuesday fell on the 28th — then the command to download worklogs for the previous month works (see above).

* The number of days for which worklogs are loaded is constant — 90 days.

* Every Tuesday night, the end date is automatically updated:
  * The end date is the current one, i.e. Tuesday of the current week.

* After updating the end date, worklogs for the specified period are loaded that same night.

* Current Tuesday's worklogs are not loading. The last day when loading worklogs will be the previous day, that is Monday.


# For developers

### How to issue or renew TLS certificates

If the launch occurs for the first time on a new server, disable SSL in nginx. it will not start without valid certificates, issue certificates with the command `docker compose run --rm certbot certonly --webroot --webroot-path /var/www/certbot/ -d jira-new-server.wbtech.pro` — your domain , then connect the config with ssl to nginx and restart the services or just nginx.

The easiest way to renew the certificate is with the nginx service running (because you need to go through the "acme-challenge") go to the code folder (or clone the repo for example) and run a command like `docker-compose run --rm certbot renew`.
Because in the certbot service, the necessary paths are mounted in nginx, then the "acme-challenge" should be resolved and the certificates will be issued.
The issued certificates are located on the host in /certbot/conf/live/... These paths are mounted in nginx read-only — for obtaining certificates. In the certbot service, these paths are also mounted, but for writing and reading — for issuing new certificates.


### How the client works

The client works in several stages.

1. First, it fetches the list of worklogs that appeared during the specified period. The period is set by query parameters in unix-time, taking into account milliseconds (therefore, we multiply by 1000). It's just a list of user information. It is needed in order to take information on worklogs with separate requests.

2. Detailed info is loaded by separate requests. A maximum of 1000 worklogs are sent in each request. Therefore, if there are more than 1000 wcrlogs in total for the specified period, a multiple requests.

3. Need more information about the tasks (issues). In info about worklogs, only indexes of tasks (such as PROJECT-001) are available. Therefore, we take all indexes from worklogs, leave unique ones and request information on tasks.

4. In total, the `get_jira_data` client method produces a tuple (worklogs, issues) with an array of two kinds of objects.


### How it works

Created a django command `python manage.py run_client <n>`, where <n> is the number of days from now to load the worklogs.

This command will delete all existing worklogs, Jira task, Finolog orders and upload new ones for the specified period.
The point is that synchronizing this information is difficult. Therefore, it was decided to simply reload daily.

Grouped worklogs can be obtained from the [main endpoint](https://jira-wl.wbtech.pro/jira-client-api/grouped-worklogs/). There you need to send the filtering parameters.

<b>Important!</b> You need to specify Jira account id, otherwise info will be immediately for all users, which is not very informative.

GET parameters: 

`updated` — select by exact worklog value of "updated"
`started` — select by exact worklog value of "started"
`created` — select by exact worklog value of "created"  
`account_id` — select by exact worklog value of "account_id"
`issue__project` — select by exact worklog value of "issue__project"

`updated_start_date`, `updated_finish_date` — selection from to by the specified parameter  
`created_start_date`, `created_finish_date` — selection from to by the specified parameter
`started_start_date` , `started_finish_date` — selection from to by the specified parameter

You can combine multiple parameters.
For example, to get a person's worklogs for a certain period, you need to send three parameters:
`started_start_date`, `started_finish_date`, `account_id`


### Additional services
In Jira and Finolog there are identical entities with different ids. For example, in Jira there is an AREND project, and in Finolog it has a digital id.
The project has models that store these mappings: `client.models.finolog.FinologProject`

In addition, there are some Jira tasks (like AREND-123), which are considered orders in Finolog.
An order is a separate accounting logic, such as a separate feature, for which the customer is paid separately.
Such matches are stored in `client.models.finolog.FinologOrder`.

Orders (`client.models.finolog.FinologOrder` instances) appear in the database at the `run_client` runtime.
Logics:
Finolog has an API method for searching orders by Jira task keys (AREND-123). That is, after we downloaded worklogs and unique tasks from Jira, we run by the names of the tasks and ask Finolog if there is such an order. If there is, save it.

#### For developers
Note that some parameters in `grouped-worklogs/` are added in the `.to_representation()` serializer.

### Addresses

jira-client-admin/ — admin panel
jira-client-api/worklogs/ — all worklogs
jira-client-api/issues/ — all tasks
jira-client-api/grouped-worklogs/ — grouped worklogs


superuser:
admin
asDqAf1SSf4

Server: 
https://jira-wl.wbtech.pro/

Admin panel:  
https://jira-wl.wbtech.pro/jira-client-admin  
admin  
asDqAf1SSf4

All Jira tasks:  
https://jira-wl.wbtech.pro/jira-client-api/issues/

All worklogs. Here it is convenient to see the filtering options for grouped worklogs:
https://jira-wl.wbtech.pro/jira-client-api/worklogs/

Main endpoint:
https://jira-wl.wbtech.pro/jira-client-api/grouped-worklogs/

Here you can see a list of all projects. You can also send data here via POST to create a new one:
https://jira-wl.wbtech.pro/jira-client-api/finolog-projects/

### Possible improvements
* enable simple token authorization


#### Launch of the run_client command

* The run_client command is automatically run once a day (via cron-command).

* The run_client command is currently passed to cron_command with no arguments.
    * If neither through the admin panel, nor manually through the console, the end date of the countdown is passed to run_client, then the current date is considered such date.
    *  <b>Important!</b> If the number of days is not passed to run_client either through the admin panel or manually through the console, then the command will not work — a custom error will appear asking you to specify the number of days.

* In order to manually pass arguments to the run_client command, you must specify --end_date {YYYY-MM-DD} and/or --days_before {number of days} respectively.
  * This is done so that the arguments are not positional and so that you can combine manually entered values with values from the admin panel.

