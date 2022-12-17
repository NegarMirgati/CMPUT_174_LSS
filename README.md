# CMPUT_174_LSS
Lost Student Support codes

## Usage

Please do the following steps:

    1. Download the eclass Roster
    2. Download the Reported Lost Students a csv file
    3. Download the previous week's Extracted Lost students Excelsheet
    4. Extract the list of students that didn't submit the last lab as a csv file ([More info about this](#helpful-tricks))
    5. Change the file names in main according to your own filenames 
    6. Check out the `is_lost` function and change it to match your desired criteria for what counts as a lost student.
    7. Check out the `change_quantile` function call. You can remove it or choose another grade item 

## Helpful Tricks

To get the list of students that did not submit a lab:

    1. Go to https://eclass.srv.ualberta.ca/mod/assign/view.php?id={lab-id}&action=grading (Lab 3)
    2. Under Options --> Filter, select Not submitted
    3. You'll get an HTML table that can be parsed. This extension worked: https://chrome.google.com/webstore/detail/ table-capture/iebpjdmgckacbodjpijphcplhebcmeop

## Requirements

Please run the following command to install the requirements:
```
pip install requirements.txt
```


