year_list=("2014" "2015" "2016" "2017" "2018" "2019")
month_list=("01","02","03","04","05","06","07","08","09","10","11","12")
for year in "${year_list[@]}"; do
    for month in "${month_list[@]}"; do
        date="${month}-${year}"
        python ../scripts/stage2.py ${date}
    done
done

python ../scripts/stage2.py ${date}
