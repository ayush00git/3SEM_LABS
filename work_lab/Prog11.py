# Program: Parse, Write, and Search XML Files
# Demonstrates XML handling using xml.etree.ElementTree

import xml.etree.ElementTree as ET

# ---------- 1. Write XML File ----------
def write_xml():
    root = ET.Element("library")

    book1 = ET.SubElement(root, "book", {"id": "1"})
    ET.SubElement(book1, "title").text = "Python Programming"
    ET.SubElement(book1, "author").text = "Guido van Rossum"

    book2 = ET.SubElement(root, "book", {"id": "2"})
    ET.SubElement(book2, "title").text = "Data Science Handbook"
    ET.SubElement(book2, "author").text = "Jake VanderPlas"

    tree = ET.ElementTree(root)
    tree.write("library.xml")
    print("✅ XML file 'library.xml' created successfully.")


# ---------- 2. Parse (Read) XML File ----------
def parse_xml():
    tree = ET.parse("library.xml")   # Load the file
    root = tree.getroot()            # Get root element

    print("\n📖 Library Books:")
    for book in root.findall("book"):
        title = book.find("title").text
        author = book.find("author").text
        print(f"- {title} by {author}")


# ---------- 3. Search in XML ----------
def search_book(title_to_find):
    tree = ET.parse("library.xml")
    root = tree.getroot()

    found = False
    for book in root.findall("book"):
        title = book.find("title").text
        author = book.find("author").text
        if title_to_find.lower() in title.lower():
            print(f"\n🔍 Found Book:\nTitle: {title}\nAuthor: {author}")
            found = True
    if not found:
        print("\n❌ Book not found.")


# ---------- Main Program ----------
if __name__ == "__main__":
    write_xml()
    parse_xml()
    search_book("Python")

