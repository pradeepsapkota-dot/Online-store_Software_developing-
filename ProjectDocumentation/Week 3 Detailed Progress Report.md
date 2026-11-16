# Software Development – Week 3 Progress Report

**Group Members:**
1. Haroon Afridi
2. Pradeep Sapkota
3. Poshan Oli
4. Lamyae Echaoui

**Week:** Week 3  
**Topic:** Python and MySQL Database Operations

---

## 1. Introduction

During Week 3, our group continued developing the Online Store Management System using Python and MySQL. The main focus was connecting Python with the MySQL database, implementing database operations, and developing the application interface.

## 2. Work Completed

The following work was completed during this period:

- Connected the Python application to the MySQL database.
- Implemented product operations, including viewing, searching, adding, and deleting products.
- Developed order management functions for creating orders and viewing order details.
- Added functionality to update order statuses.
- Implemented payment recording and payment information display.
- Connected the backend functions with the Streamlit application.
- Improved the application interface to make it easier to use.
- Tested the main application functions and checked database operations.

## 3. Team Members' Contributions

### Haroon Afridi
Completed the  application development work. Main contributions included:

- Developing the Streamlit application interface.
- Connecting the application with the Python backend and MySQL database.
- Implementing and integrating product, order, and payment features.
- Improving the application workflow and handling different operations.
- Testing the application and fixing issues.

### Pradeep Sapkota
Pradeep contributed to the development of the Online Store Management System, mainly working on the application interface and supporting its development. He helped implement and improve some application features alongside Haroon. He also participated in discussions about the application workflow and functionality. His work supported the integration of the different parts of the system.

### Poshan Oli
Provided support mainly related to the order management part of the project and discussions about its functionality.

### Lamyae Echaoui
Provided support with reviewing the application and checking whether its main features worked correctly. Supporting the preparation and organization of project documentation. Reviewing the project progress and discussing possible improvements with the team.

## 4. Application Progress

The Online Store Management System now has a working Streamlit interface connected to the MySQL database.

The application supports:

- Product management
- Creating customer orders
- Viewing order details
- Updating order status
- Recording payments
- Viewing payment status and payment method

The application also automatically changes an order from **Pending** to **Processing** after a successful payment.


## 5. Application Screenshots

### Figure 1 – Product Management

This screenshot shows the product list, including product names, prices, categories and available stock.

![Product Management](../ApplicationScreenshots/product-management.png)

### Figure 2 – Create Order

This screenshot shows the order creation page where customers and products can be selected.

![Create Order](../ApplicationScreenshots/create-order.png)

### Figure 3 – Order Management

This screenshot shows the order list and order status management.

![Order Management](../ApplicationScreenshots/order-management.png)

### Figure 4 – Payment Management

This screenshot shows payment information, including payment method, amount and payment status.

![Payment Management](../ApplicationScreenshots/payment-management.png)


## 6. Testing
New tests were made this week regarding searching, deleting, adding products:

### 6.1 Searching Products
when searching for a product, it suggests two options: search by name or search by ID
Example used here was Wireless mouse and the product info is displayed then successfully
Same with searching using product ID, the ID number is added (Wireless mouse ID: 1) the product info is also displayed.

### 6.2 Deleting Products
The product deletion functionality was tested by selecting an existing product from the product list. The selected product was the Mechanical Keyboard (Product ID: 2).
After confirming the deletion, the application displayed an error message indicating that the product could not be deleted because it was linked to an existing order.
This error was caused by a foreign key constraint between the product and orderitem tables. The database prevents the deletion of products that are referenced by existing order records to maintain referential integrity.

### 6.3 Adding Products
The product addition functionality was tested by entering the required product information, including the product name, category, price, and stock quantity.
The application successfully added the new product to the database. However, no confirmation message was displayed after submitting the form. To verify that the operation was successful, it was necessary to navigate to the Products List and check whether the newly added product appeared.
Another issue was identified when attempting to add a product that already existed in the database. Instead of updating the stock quantity of the existing product, the application created a new product entry with a different Product ID.
This resulted in multiple entries for the same product in the product list, as observed during testing with the Mouse Pad product.

### 6.4 Creating orders
The order creation functionality was tested by selecting an existing customer and adding a product to the order.

For this test, Michael Brown (Customer ID: 3) was selected, and a Laptop Stand (Product ID: 4) was added with a quantity of 1.

The application correctly displayed the product price (€39.99), available stock (200 units), and calculated the order total (€39.99).

However, after clicking the "Create Order" button, the application displayed an error message indicating that order creation had failed.

Although the customer and product selection, quantity input, and total price calculation worked correctly, the order could not be successfully submitted.

Further investigation is required to identify the cause of the failure.

## 7. Conclusion

During Week 3, we made good progress on the Online Store Management System. We developed the main application features using Python, MySQL, and Streamlit. The system now supports product management, order creation, order tracking, and payment recording. We also improved the application by displaying payment details and automatically changing an order's status from Pending to Processing after successful payment.

In addition, we created automated tests using pytest to check the main product, order, and payment functions. All 17 automated tests passed successfully. We also improved the project documentation and uploaded the latest changes to GitHub. Overall, this week's work helped us build a more functional and organized application. In the next stage, we plan to continue improving the system, review the code, and work on the remaining project requirements.
