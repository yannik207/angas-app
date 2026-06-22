1. The Setup & Auto-Instrumentation

Figure out which OpenTelemetry package you need to install to automatically instrument FastAPI.

Configure your app to print trace data to the console.

Apply the instrumentation to your app instance.

Test: If you run your server and send a POST request to http://127.0.0.1:8000/orders/42, you should automatically see a massive span generated in your console representing the HTTP request, without you writing any manual span code!

2. The Manual Internal Span

The auto-instrumentation won't track the specific time spent inside check_inventory. You need to do that manually.

Get a tracer instance in your file.

Wrap the logic inside check_inventory in a new, manual span named inventory.db_check. This span should automatically become a child of the FastAPI HTTP request span.

3. The Metadata

Add a custom attribute to your manual inventory.db_check span called shop.item_id that records the ID being checked.

4. The Error State

Trigger the error by sending a POST request to http://127.0.0.1:8000/orders/999.

Ensure that your manual inventory.db_check span properly catches the ValueError, records it as an event, and marks the span's status as an error.