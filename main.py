import os
import csv
from bs4 import BeautifulSoup

def evaluate(soup,file_name):
    tables = soup.findAll('table')
    results = []
    for table in tables:
        rows = table.find_all('tr')
        for index, row in enumerate(rows):
            if "per share" in row.get_text().lower() or "per common share" in row.get_text().lower() or "per ordinary share" in row.get_text().lower():
                num_not_found = False
                # Find the cell with the value in the same row
                cells = row.find_all('td')

                text = ""

                for idx, cell in enumerate(cells):
                    if cell.get_text(strip=True).replace("\xa0","").replace("\n","").replace(" ","").replace("(", "").replace(")","").replace(",", "").replace("$", "").replace(".", "").isnumeric():
                        if "(" in cell.get_text(strip=True):
                            value = "-"+cell.get_text(strip=True).replace("(", "").replace(")","")
                        else:
                            value = cell.get_text(strip=True)

                        num_not_found = True

                        for i in range(idx):
                            text = text + " " + cells[i].get_text(strip=True)
                        results.append({"value": value.replace("\xa0", "").replace("\n", "").replace(" ", "").replace(
                                    "(", "").replace(")", "").replace(",", "").replace("$", ""), "row": text})
                        break

                if not num_not_found and index < len(rows) - 1:
                    newcells = rows[index + 1].find_all('td')
                    for idx2,cell in enumerate(newcells):
                        if cell.get_text(strip=True).replace("\xa0","").replace("\n","").replace(" ","").replace("(", "").replace(")","").replace(",", "").replace("$", "").replace(".", "").isnumeric():
                            if "(" in cell.get_text(strip=True):
                                value = "-" + cell.get_text(strip=True).replace("(", "").replace(")", "")
                            else:
                                value = cell.get_text(strip=True)

                            for i in range(len(cells)):
                                text = text + " " + cells[i].get_text(strip=True)

                            for i in range(idx2):
                                text = text + " " + newcells[i].get_text(strip=True)

                            num_not_found=True

                            results.append({"value": value.replace("\xa0", "").replace("\n", "").replace(" ", "").replace(
                                    "(", "").replace(")", "").replace(",", "").replace("$", ""), "row": text})
                            break

                    if not num_not_found and index < len(rows) - 2:
                        newcells2 = rows[index + 1].find_all('td')
                        for idx3, cell in enumerate(newcells2):
                            if cell.get_text(strip=True).replace("\xa0", "").replace("\n", "").replace(" ", "").replace(
                                    "(", "").replace(")", "").replace(",", "").replace("$", "").replace(".",
                                                                                                        "").isnumeric():
                                if "(" in cell.get_text(strip=True):
                                    value = "-" + cell.get_text(strip=True).replace("(", "").replace(")", "")
                                else:
                                    value = cell.get_text(strip=True)

                                for i in range(len(cells)):
                                    text = text + " " + cells[i].get_text(strip=True)

                                for i in range(len(newcells)):
                                    text = text + " " + newcells[i].get_text(strip=True)

                                for i in range(idx3):
                                    text = text + " " + newcells2[i].get_text(strip=True)

                                num_not_found = True

                                results.append({"value": value.replace("\xa0", "").replace("\n", "").replace(" ", "").replace(
                                    "(", "").replace(")", "").replace(",", "").replace("$", ""), "row": text})
                                break


    length = len(results)
    if length == 1:
        return results[0]["value"]
    elif length > 1:
        newresults = []
        for result in results:
            text = result["row"].lower()
            if "earnings" in text or "basic" in text or "loss" in text:
                newresults.append(result)

        if len(newresults)==1:
            return newresults[0]["value"]
        elif len(newresults)>1:
            lastresults=[]
            for result in newresults:
                text = result["row"].lower()
                if "basic" in text and "dilute" in text:
                    lastresults.append(result)
                elif("basic" not in text and "dilute" in text):
                    continue
                elif "non gaap" in text or "non-gaap" in text:
                    continue
                elif "shares" in text:
                    continue
                else:
                    lastresults.append(result)

            if len(lastresults)==0:
                print("nofound", file_name)
                return

            return lastresults[0]["value"]
        elif len(newresults)==0:
            print("nofound",file_name)
            return
        return newresults[0]["value"]
    else:
        print("nofound",file_name)
def parse_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

        return evaluate(soup,file_path)


def process_filings(input_folder, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['filename', 'EPS']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for filename in os.listdir(input_folder):
            if filename.endswith(".html"):
                file_path = os.path.join(input_folder, filename)
                eps_value = parse_html(file_path)

                # Write filename and EPS value to CSV
                writer.writerow({'filename': filename, 'EPS': eps_value})


if __name__ == "__main__":
    input_folder = "./Training_Filings"
    # input_folder = "./temp"
    output_file = "output_example.csv"

    process_filings(input_folder, output_file)
