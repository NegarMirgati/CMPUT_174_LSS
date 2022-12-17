# CMPUT_174_LSS
Lost Student Support codes

## Usage

Please do the following steps:

0. Go to DocsDB -> Mark Posting and check `Post sections in separate reports` and `By Total` and download the html
1. Copy the field names e.g., Student Id, CCid, Lab1, Lab2, ...
2. Remove all the html tags from the html file to make it like a simple list of records 
3. Download the eclass Roster
4. Download the Reported Lost Students (by TAs) a csv file
5. Download the previous week's Extracted Lost students Excelsheet
6. Extract the list of students that didn't submit the last lab as a csv file ([more info about this](#helpful-tricks))
7. Change the file names in the `main` function according to your own filenames 
8. Change the `col_names` variable at the top of the script according to step 1
9. Check out the `is_lost` function and change it to match your desired criteria for what counts as a lost student.
10. Check out the `change_quantile` function call. You can remove it or choose another grade item 

## Helpful Tricks

To get the list of students that did not submit a lab:

1. Go to https://eclass.srv.ualberta.ca/mod/assign/view.php?id={lab-id}&action=grading (change lab-id to go to a specific lab's page)
2. Under Options --> Filter, select Not submitted
3. You'll get an HTML table that can be parsed. 
4. Check out [This extension](https://chrome.google.com/webstore/detail/table-capture/iebpjdmgckacbodjpijphcplhebcmeop) worked. 

## Requirements

Please run the following command to install the requirements:
```
pip install requirements.txt
```
