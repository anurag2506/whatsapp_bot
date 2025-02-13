<h1>WhatsApp Smart Bot</h1>
<h3><b>Project Description</b></h3>
<p>This project aims at building a WhatsApp bot capable of storing your messages regarding any expense you make throughout your day. It can answer any question regarding these expenses
and provide relevant insights. This will make managing your finances a breeze and save you time of accounting and tracking.</p>

<h3><b>Basic Workflow of the Project</b></h3>
<p>The workflow starts off by the user sending a message like "Spent 300 on Coffee" and the relevant categories like: 
<br> 1. Amount <br> 2. Category <br> 3. Description <br> are stored in the Postgress DB</p>
<br><b> The choice of Postgres was clear because of easy SQL query look up and also because of its ability to store JSON objects. And also time-based querying was also possible.</b><br>

<p><b>The next step is to run Llama 3.2 7B on the input message and check whether the input message is a query or an expense instruction.</b> If the message is a query, then the whole DB is iterated in the ``` python respond ``` route of the flask service and given to the LLM for processing Natural Language and then a relevant response is generated and sent to the user via WhatsApp.<br>If the message is a instruction, then it is made to pass through the ``` python add_expense ``` route. <br> All of this happens via the Twilio Sandbox for the WhatsApp API</p>

<h3><b>Extra Features for Increasing the UI</b></h3>

<p>
1. Adding Charts to visualise the expenses better<br>
2. Starting the chat by letting the user choose the language of their choe  and then process every query in that language<br>
3. Using Basic solidity contracts for Authentication<br>
4. Adding a scheduler using Celery, Cron Jobs to automate the expenses report to the user(either on a daily or a weekly basis)<br>
</p>
