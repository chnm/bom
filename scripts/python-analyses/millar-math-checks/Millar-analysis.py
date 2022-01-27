# import modules
import csv

# define function for generalized case
def check_math(file):
    # open and read the transcription file, create Header Row for export .csv
    transcription = open(file)
    dataset = csv.reader(transcription)

    export_file_name = file[:-4] + "_math_check.csv"
    results = open(export_file_name, 'a+')
    results.write('id,in_walls_calculated,in_walls_given,in_walls_TF,out_walls_calculated,out_walls_given,out_walls_TF,middlesex_surrey_calculated,middlesex_surrey_given,middlesex_surrey_TF,westminster_calculated,westminster_given,westminster_TF,all_christenings_calculated,all_burials_calculated\n')

    j = 0

    # calculated subunit sums for each bill of mortality
    for bill in dataset:
    
        # skip first/header row
        if j == 0:
            j = j + 1
            continue
    
        unique_id = bill[4]
        
        i = 11
        in_walls = 0
        while i < 109:
            if bill[i] != '':
                in_walls = in_walls + int(bill[i])
            i = i + 1
        print(in_walls)
        
        i = 112
        out_walls = 0
        while i < 129:
            if bill[i] != '':
                out_walls = out_walls + int(bill[i])
            i = i + 1
        print(out_walls)
            
        i = 133
        middlesex_surrey = 0
        while i < 155:
            if bill[i] != '':
                middlesex_surrey = middlesex_surrey + int(bill[i])
            i = i + 1
        print(middlesex_surrey)

        i = 158       
        westminster = 0
        while i < 168:
            if bill[i] != '':
                westminster = westminster + int(bill[i])
            i = i + 1
        print(westminster)
        
        all_christened = int(bill[109]) + int(bill[130]) + int(bill[155]) + int(bill[169])
        all_buried = int(bill[110]) + int(bill[131]) + int(bill[156]) + int(bill[170])
        
        # check calculated sums against printed sums in bill of mortality
        if in_walls == int(bill[110]):
            iw = "true"
        else:
            iw = "false"
        if out_walls == int(bill[131]):
            ow = "true"
        else:
            ow = "false"
        if middlesex_surrey == int(bill[156]):
            ms = "true"
        else:
            ms = "false"
        if westminster == int(bill[170]):
            wm = "true"
        else:
            wm = "false"
        
        # write results to export file
        results.write(unique_id + ',' + str(in_walls) + ',' + bill[110] + ',' + iw + ',' + str(out_walls) + ',' + bill[131] + ',' + ow + ',' + str(middlesex_surrey) + ',' + bill[156] + ',' + ms + ',' + str(westminster) + ',' + bill[170] + ',' + wm + ',' + str(all_christened) + ',' + str(all_buried) + '\n')
    
    # close files
    transcription.close()
    results.close()
    
# end function definition

#begin program
#file_name = input('What is the exact name of your csv file (include the .csv) ')
file_name = "Millar.csv"
check_math(file_name)

# end program