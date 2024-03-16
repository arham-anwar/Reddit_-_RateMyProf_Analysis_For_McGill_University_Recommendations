from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time

# Rate My Professors McGill URL
url = 'https://www.ratemyprofessors.com/search/professors/1439?q=*'

# Set up the WebDriver
driver = webdriver.Chrome()

driver.get(url)

# Wait for the page to load
time.sleep(10)

while True:
    try:
        # Find the "Show More" button and click it
        show_more_button = driver.find_element('xpath', '/html/body/div[2]/div/div/div[4]/div[1]/div[1]/div[5]/button')
        print(show_more_button)
        show_more_button.click()
        # Wait for the page to load more content
        time.sleep(3)
    except (NoSuchElementException, ElementClickInterceptedException):
        # Find the container div by XPath
        container_div = driver.find_element('xpath', '/html/body/div[2]/div/div/div[4]/div[1]/div[1]/div[4]')
        # Find all anchor tags within this div
        anchor_tags = container_div.find_elements('tag name', 'a')
        # Extract the href attributes and store them in a list
        href_list = [anchor.get_attribute('href') for anchor in anchor_tags]
        # Create a DataFrame from the list
        df_links = pd.DataFrame(href_list, columns=['Links'])
        # Save the DataFrame to a CSV file
        df_links.to_csv('professor_links.csv', index=False)
        # Print the list and its length
        print("Total links found:", len(href_list))
        print("Links saved to professor_links.csv")
        break  # Exit the loop

# Clean up
driver.quit()

# Read the CSV file with the professor links into a DataFrame
df_professor_links = pd.read_csv('professor_links.csv')

# Initialize a list to hold all the scraped data
all_professor_data = []

# Iterate through the DataFrame with the professor links
for link in df_professor_links['Links']:
    # Make a GET request to the professor's page
    response = requests.get(link)

    # If the request was successful, proceed to scrape the content
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        try:
            # Find all comments
            comments = soup.find_all('div', class_='Comments__StyledComments-dzzyvm-0')
            department = soup.find('a', class_='TeacherDepartment__StyledDepartmentLink-fl79e8-0').text.strip()
            school = soup.find('a', href="/school/1439").text.strip()
            professor_name = ' '.join([
                soup.find('div', class_='NameTitle__Name-dowf0z-0').text.strip(),
                soup.find('span', class_='NameTitle__LastNameWrapper-dowf0z-2').text.strip()
            ])

            # Loop through all comments and add them to the list along with other details
            for comment in comments:
                comment_text = comment.text.strip()
                print(comment_text, department, school, professor_name)
                all_professor_data.append({
                    'Comment': comment_text,
                    'Department': department,
                    'School': school,
                    'ProfessorName': professor_name
                })

        except Exception as e:
            print(f"An error occurred while processing the page: {link}")
            print(f"Error: {e}")

# Create a DataFrame from the scraped data
df_all_professor_data = pd.DataFrame(all_professor_data)

# Save the DataFrame to a new CSV file
df_all_professor_data.to_csv('all_professor_comments.csv', index=False)

# Print the shape of the DataFrame and the first few rows to check
print("DataFrame Shape:", df_all_professor_data.shape)
print(df_all_professor_data.head())
