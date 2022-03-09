

### Как работает клиент

Клиент работает в несколько этапов. 

1. Сначала фетчит список ворклогов, появившийся за указанный период. Период задается 
параметрами запроса в unix-time с учетом миллисекунд (поэтому умножаем на 1000). Это 
просто список юез информации. Он нужен, чтобы отдельными запросами взять инфу по 
ворклогам.

2. Подробная инфа грузится отдельными запросами. В каждом запросе передается максимум 
1000 ворклогов. Поэтому, если всего за указанный период больше 1000 вокрлогов, создается
несколько запросов. 

3. Нужна еще информация о задачах  (issues). В инфо о ворклогах доступны только индексы
задач (типа ПРОЕКТ-001). Поэтому берем все индексы из ворклогов, оставляем уникальные и
запрашиваем инфу по задачам. 

4. Итого, метод клиента `get_jira_data` выдает кортеж (worklogs, issues) с массивом объектов
двух видов. 


### Как вообще работает
Создана джанго-комманда 
``` python manage.py run_client <n> ```  
где n - это количество дней от текущего момента, за который нужно загрузить ворклоги. 

Эта команда удаляте все существующие ворклоги, таски жиры, заказы финолога.
И загружает новые за указанный период.  
Смысл в том, что синхронизировать эту информацию сложно. Поэтому решено просто 
ежедневно загружать заново. 

По основному ендпоинту  
```https://jira-wl.wbtech.pro/jira-client-api/grouped-worklogs/```  
можно получить сгруппированные ворклоги. Туда нужно отправить параметры фильтрации.  
Важно!!! Нужно указывать jira account_id, иначе инфа придет сразу по всем пользователям, 
что малоинформативно. 
GET параметры: 

```updated``` - выборка по точному значению updated ворклога  
```started``` - выборка по точному значению started ворклога  
```created``` - выборка по точному значению created ворклога  
```account_id``` - выборка по точному значению account_id ворклога  
```issue__project```  - выборка по точному значению issue__project ворклога  

``updated_start_date``, ```updated_finish_date``` - выборка от до по указанному параметру  
```created_start_date```, ```created_finish_date``` - выборка от до по указанному параметру  
```started_start_date``` , ```started_finish_date``` - выборка от до по указанному параметру  

Можно комбинировать несколько параметров.
Например, чтобы получить ворклоги человека за определенный период, нужно отправить три параметра: 
```started_start_date```, ```started_finish_date```, ```account_id```


### Дополнительные сервисы
В жире и финологе есть одинаковые сущности с разными айдишниками. Например, в жире есть
проект AREND, и в финологе у него есть цифровой id. 
В проекте есть модели, которые хранят такие соответствия: 
`client.models.finolog.FinologProject`

Кроме того, есть некоторые jira таски (вида AREND-123), которые в финологе считаются заказами.  
`Заказ - это отдельная логика учета, типа отдельной фичи, за которую с заказчиком отдельно 
расплачиваются`  
Такие соответствия хранятся в `client.models.finolog.FinologOrder`

Заказы (инстансы `client.models.finolog.FinologOrder`) появляются в БД на этапе выполнения 
`run_client`. Логика:  
В финологе есть api метод для поиска заказов по jira ключам тасков (AREND-123). Т.е. после того,
как скачали с жиры ворклоги и уникальные таски, бежим по именам тасков и спрашиваем финолог - 
есть ли такой заказ. Если есть, сохраняем. 

#### Для разработчиков
Обратите внимание, что некоторые параметры в `grouped-worklogs/` подставляются в сериализаторе
в `.to_representation()`

### Адреса

jira-client-admin/ - админка
jira-client-api/worklogs/ - все ворклоги
jira-client-api/issues/ - все таски
jira-client-api/grouped-worklogs/ - сгруппированные ворклоги


superuser:
admin
asDqAf1SSf4


Сервер  
https://jira-wl.wbtech.pro/

Админка  
https://jira-wl.wbtech.pro/jira-client-admin  
admin  
asDqAf1SSf4

Все таски из жиры  
https://jira-wl.wbtech.pro/jira-client-api/issues/

Все ворклоги. Здесь удобно посмотреть параметры фильтрации для группированных ворклогов  
https://jira-wl.wbtech.pro/jira-client-api/worklogs/

Основной ендпоинт  
https://jira-wl.wbtech.pro/jira-client-api/grouped-worklogs/

Здесь можно посмотреть список всех проектов. Сюда же через POST можно отправить 
данные для создания нового  
https://jira-wl.wbtech.pro/jira-client-api/finolog-projects/

### Возможные доделки
* включить простую токен авторизацию

### Указание количества дней и стартовой даты отсчета для загрузки ворклогов

* На главной странице админ-панели (jira-client-admin/) в приложении Client создан пункт «! Период, за которые необходимо загрузить ворклоги».


* При нажатии на пункт открывается страница с двумя полями ввода (jira-client-admin/client/daysfordownloadmodel/worklogs-download-period/).


* В полях отображаются текущее количество дней, за которое необходимо скачать ворклоги, и стартовая дата отсчета, введенные через админку.


* <b>Важно!</b> Если при вызове команды run_client в терминале вручную указано количество дней и/или стартовая дата, то они имеют приоритет над значениями, заданными через админку.
  
    * Дефолтная (применяющаяся в том случае, если через админ-панель или при вызове команды run_client вручную не указано иное) стартовая дата отсчета — текущая. 
  
    * Дефолтное количество дней, за которое необходимо загрузить ворклоги, не установлено. Без указания на количество дней загрузка ворклогов не будет работать — необходимо либо установить его через админ-панель, либо вручную передать django-команде run_client в качестве аргумента.


* Если формы в админке пустые, то в текущий момент количество дней для загрузки ворклогов и стартовая дата не установлены.


* Для установки/изменения количества дней и стартовой даты необходимо ввести в соответствующие поля целое число/дату и нажать «Отправить».
    * Стартовая дата указывается в формате YYYY-MM-DD.
  
    * Количество дней не должно превышать 3 месяца с указанной даты. То есть, к примеру, при стартовой дате 2022-02-01 ворклоги могут быть отображены только во временном диапазоне с 2022-01-31 по 2021-11-01 включительно.
  

* Установленные через админ-панель параметры сохраняются и не сбрасываются автоматически.
  * Заданные значения будут применяться до их изменения или удаления. 


* В том случае, если необходимо удалить значение(-ия), необходимо ввести в соответствующее(-ия) поле(-я) пустую строку и нажать «Отправить».

#### Запуск команды run_client

* Команда run_client автоматически запускается раз в сутки (через cron-command).


* В настоящий момент в cron_command команда run_client передана без аргументов.
    * Если ни через админку, ни вручную через консоль в run_client не передана стартовая дата отсчета, то такой датой считается текущая.
    * <b>Важно!</b> Если ни через админку, ни вручную через консоль в run_client не передано количество дней, то команда не будет работать — вылезет кастомная ошибка с просьбой указать количество дней.


* Для того, чтобы передать аргументы команде run_client вручную, необходимо указать --start-date {YYYY-MM-DD} и/или --days_before {кол-во дней} соответственно.
  * Это сделано для того, чтобы аргументы не были позиционными и чтобы можно было комбинировать значения, введенные вручную, со значениями из админки.