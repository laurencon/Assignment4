from bs4 import BeautifulSoup
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["web_crawler"]
collection = db["pages"]
professors = db["professors"]

def parse_faculty(html):
    bs = BeautifulSoup(html, 'html.parser')
    faculty = bs.find('section', class_='text-images', id='s0')

    if not faculty:
        print("Faculty section not found in HTML.")
        return []
    
    faculty_list = []

    faculty_members = faculty.find_all('div', class_='clearfix')
    if not faculty_members:
        print("No faculty members")
        return []
    for member in faculty_members:
        name_e = member.find('h2')
        if name_e:
            name = name_e.text.strip()
        else:
            print("Name not found for a faculty member")
            continue
        
        faculty_info = {
            "name" : name,
            
        }
        for p in member.find_all('p'):
            strong_tag = p.find('strong')
            if strong_tag:
                key = strong_tag.text.strip().rstrip(':')
                value = strong_tag.next_sibling.strip()
                faculty_info[key.lower()] = value

        email_e = member.find('a', href=lambda x: x and x.startswith('mailto:'))
        faculty_info["email"] = email_e['href'].strip().replace('mailto:', '') if email_e else None

        website_e = member.find('a', href=lambda x: x and not x.startswith('mailto:'))
        faculty_info["website"] = website_e['href'].strip() if website_e else None

        faculty_list.append(faculty_info)
    return faculty_list

def insert_faculty(faculty_list):
    for faculty_info in faculty_list:
        professors.insert_one(faculty_info)
        print(f"Faculty member {faculty_info['name']} inserted into Mongo")

def main():
    TARGET = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"
    page = collection.find_one({"url": TARGET})

    if not page:
        print(f"HTML data for {TARGET} not found")
        return
    html = page.get('html', '')
    faculty_list = parse_faculty(html)

    if not faculty_list:
        print("No faculty info parsed")
        return
    insert_faculty(faculty_list)

if __name__ == "__main__":
    main()