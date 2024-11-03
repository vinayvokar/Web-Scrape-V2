from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import csv
import json
import random
import pandas as pd

import streamlit as st

status_message = st.empty()

def fetch_data(n):
    status_message.info("fetching categories ...")
    web.find_element(By.XPATH, "//a[text()='Best Sellers']").click()
    time.sleep(2)
    category_elements = web.find_elements(By.XPATH, "//div[@role='treeitem']//a")

    # Extract the links of the categories
    category_links = [elem.get_attribute("href") for elem in category_elements if elem.is_displayed()]

    # Fetch random 10 links
    random_category_links = random.sample(category_links, min(10, len(category_links)))

    # Store the random links in a list
    stored_links = list(random_category_links)

    # List to store product data
    product_data = []


    for category_url in stored_links:
        web.get(category_url)
        time.sleep(2)  # Wait for the page to load

        # Extracting category name
        category_name = category_url.split('/')[-2].capitalize()

        for page_number in range(1,n+1):
            # Update the URL to point to the correct page
            paginated_url = f"{category_url}?page={page_number}"
            web.get(paginated_url)
            status_message.info(f"fetching data of {category_name} from page : {page_number}!")
            time.sleep(2)
            try:
                products = web.find_elements(By.CLASS_NAME, '_cDEzb_p13n-sc-css-line-clamp-3_g3dy1')  # Product titles
                prices = web.find_elements(By.CLASS_NAME, '_cDEzb_p13n-sc-price_3mJ9Z')  # Product prices
                No_of_rating = web.find_elements(By.XPATH, "//span[@class='a-size-small']")  # Sale discounts
                ratings = web.find_elements(By.XPATH,
                                            "//i[@class='a-icon a-icon-star-small a-star-small-3-5 aok-align-top']/span[@class='a-icon-alt']")  # Product ratings
                descriptions = web.find_elements(By.CLASS_NAME,
                                                 '_cDEzb_p13n-sc-css-line-clamp-3_g3dy1')  # Product descriptions

                # Loop through products and extract details
                for i in range(len(products)):
                    product_info = {
                        'name': 'N/A',  # Default value
                        'price': 'N/A',
                        'No_of_rating': 'N/A',
                        'rating': 'N/A',
                        'description': 'N/A',
                        'category': category_name,
                    }

                    try:
                        product_info['name'] = products[i].text
                    except IndexError:
                        pass  # Default value remains 'N/A'

                    try:
                        product_info['price'] = prices[i].text
                    except IndexError:
                        pass

                    try:
                        product_info['No_of_rating'] = No_of_rating[i].text if i < len(No_of_rating) else "N/A"
                    except IndexError:
                        pass

                    try:
                        product_info['rating'] = ratings[i].text if i < len(ratings) else "N/A"
                    except IndexError:
                        pass

                    try:
                        product_info['description'] = descriptions[i].text if i < len(descriptions) else "N/A"
                    except IndexError:
                        pass

                    # Append the product information to the list
                    product_data.append(product_info)
                    status_message.info("fetching data ...")

            except Exception as e:
                print(f"An error occurred while processing category {category_name}: {e}")
                continue  # Move on to the next category

    df = pd.DataFrame(product_data)
    status_message.success("data fetched!")
    # Streamlit App
    st.title("Product Information Table")

    # Display the table
    st.write("### Product Details")
    st.dataframe(df)
    # Save the product data to CSV
    csv_file_path = 'product_data.csv'
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'price', 'No_of_rating', 'rating',
                      'description', 'category']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for item in product_data:
            writer.writerow(item)

    st.write(f"Product data saved to {csv_file_path}")

    # Save the product data to JSON
    json_file_path = 'product_data.json'
    with open(json_file_path, mode='w', encoding='utf-8') as jsonfile:
        json.dump(product_data, jsonfile, ensure_ascii=False, indent=4)

    st.write(f"Product data saved to {json_file_path}")








def scraper(email,password):
    # Click the account list to log in
    web.find_element(By.ID, 'nav-link-accountList-nav-line-1').click()
    # Locate the email input field and enter email/phone
    email_field = web.find_element(By.ID, 'ap_email')
    email_field.send_keys(email)  # Replace with your email/phone number
    time.sleep(2)
    # Click the 'Continue' button
    web.find_element(By.ID, 'continue').click()

    # Allow some time for next page to load
    time.sleep(2)

    # Locate the password input field and enter the password
    password_field = web.find_element(By.ID, 'ap_password')
    password_field.send_keys(password)  # Replace with your Amazon password

    # Click the 'Sign-In' button
    web.find_element(By.ID, 'signInSubmit').click()

    # Wait for the login process to complete
    time.sleep(5)

    # Verify if logged in successfully
    if "Your Account" in web.page_source:
        status_message.success('Login successful!')
    else:
        status_message.warning("Login failed, check credentials or 2FA.")
        time.sleep(30)




st.title("Amazon Bestsellers Web Scraper")
website=st.text_input("Enter the  amazon website URL")
email = st.text_input("Enter the email address")
password = st.text_input("Enter the password",type="password")
n = st.text_input("Enter the number of page you want to scrap: (1-10)")
if n:
    n = int(n)

if st.button("Scrape Now"):
    # Setup service and initialize the Chrome browser
    service = Service(ChromeDriverManager().install())
    web = webdriver.Chrome(service=service)

    # Navigate to Amazon's homepage
    web.get(website)

    # Maximize browser window
    web.maximize_window()

    # Allow the page to load
    time.sleep(2)

    status_message.success('Loading complete!')
    scraper(email,password)

    fetch_data(n)

    file_path1 = "product_data.json"

    # Read the file content
    with open(file_path1, "r") as file:
        file_content = file.read()

    # Create a download button for the file
    st.download_button(
        label="Download JSON File",
        data=file_content,
        file_name="product_data.json",  # The name for the downloaded file
        mime="application/json"
    )

    file_path2 = "product_data.csv"

    # Read the file content
    with open(file_path2, "r") as file:
        file_content = file.read()

    # Create a download button for the CSV file
    st.download_button(
        label="Download CSV File",
        data=file_content,
        file_name="product_data.csv",  # The name for the downloaded file
        mime="text/csv"
    )
















