<h1>WhatsApp Smart Bot</h1>
<h3><b>Project Description</b></h3>
<p>This project aims at building a WhatsApp bot capable of storing your messages regarding any expense you make throughout your day. It can answer any question regarding these expenses
and provide relevant insights. This will make managing your finances a breeze and save you time of accounting and tracking.</p>

<h3><b>Basic Workflow of the Project</b></h3>
<p>The workflow starts off by the user sending a message like "Spent 300 on Coffee" and the relevant categories like: 
<br> 1. Amount <br> 2. Category <br> 3. Description <br> are stored in the Postgress DB</p>
<br><b> The choice of Postgres was clear because of easy SQL query look up and also because of its ability to store JSON objects. And also time-based querying was also possible.</b><br><br>

<h3><b>Role of Natural Language in the entire process</b></h3><br>
<p><b>The next step is to run Llama 3.2 7B on the input message and check whether the input message is a query or an expense instruction.</b> If the message is a query, then the whole DB is iterated in the <b> 'process_query' </b> route of the flask service and given to the LLM for processing Natural Language and then a relevant response is generated and sent to the user via WhatsApp.<br>If the message is a instruction, then it is made to pass through the <b>'add_expense'</b> route.   
All of this happens via the Twilio Sandbox for the WhatsApp API to fetch messages from the user and provide the response. </p>

<h3><b>Things to Improve On:</b></h3>
<p>
  1. Generality of queries <br>
  2. Questions that require really complex queries for fetching results<br>
  3. Adding a scheduler that automatically calls the endpoint to start the service so that users can start off messaging whenever 
</p>

<h3><b>Extra Features to Enhance the model</b></h3>
<p>
1. Adding Charts to visualise the expenses better<br>
2. Starting the chat by letting the user choose the language of their choe  and then process every query in that language<br>
3. Using Basic solidity contracts for Authentication<br>
4. Adding a scheduler using Celery, Cron Jobs to automate the expenses report to the user(either on a daily or a weekly basis)<br>
</p>



