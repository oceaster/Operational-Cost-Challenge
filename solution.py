"""
Please write you name here: Owen Easter
"""

import csv
from datetime import datetime


def make_daily_report(start=9, end=23, default_value=float()):
    report = dict()
    for hour in range(start, end):
        if hour < 10: hour = '0' + str(hour)
        report[str(hour) + ':00'] = default_value
    return report


def process_shifts(path_to_csv):
    business_day = make_daily_report()
    shift_file = open(path_to_csv, 'r')
    shift_table = csv.DictReader(shift_file)

    for shift in shift_table:
        
        shift_start = datetime.strptime(
            shift['start_time'], "%H:%M"
        )
        shift_end = datetime.strptime(
            shift['end_time'], "%H:%M"
        )
        break_data = shift['break_notes'].\
            replace('.', ':').\
            replace(' ', '').\
            split('-')
        
        # Parse and Universalize Break Time Data
        for index, raw_data in enumerate(break_data):
            time = raw_data.\
                replace('PM', '').replace('AM', '')
        
            if ':' in time:
                time = time.split(':')
            else:
                time = [time, '00']
        
            # if time before earliest time or PM specified -> time is PM
            if int(time[0]) < 9 or 'PM' in raw_data[index]:
                time[0] = str( int(time[0]) + 12 )
            # Submit new format
            break_data[index] = ':'.join(time)

        break_start = datetime.strptime(
            break_data[0], "%H:%M"
        )
        break_end = datetime.strptime(
            break_data[1], "%H:%M"
        )

        pph = float(shift['pay_rate'])  # Pay per hour
        ppm = pph / 60                  # Pay per minute

        for hour in business_day:
            hours = datetime.strptime(hour, "%H:%M")
            pay = 0

            if break_start <= hours < break_end:
                if break_start.hour == hours.hour:
                    pay += ppm * break_start.minute
                if break_end.hour == hours.hour:
                    pay += ppm * (60 - break_end.minute)

            elif shift_start <= hours < shift_end:
                pay += pph
                if shift_start.hour == hours.hour:
                    pay -= ppm * shift_start.minute
                if shift_end.hour == hours.hour:
                    pay -= ppm * (60 - shift_end.minute)
            
            business_day[hour] += round(pay, 2)

    return business_day


def process_sales(path_to_csv):
    business_day = make_daily_report()
    sales_file = open(path_to_csv, 'r')
    sales = csv.DictReader(sales_file)
    
    for sale in sales:
        hour = sale['time'].split(':')[0] + ':00'
        business_day[hour] += float(sale['amount'])
        business_day[hour] = round(business_day[hour], 2)
    
    return business_day


def compute_percentage(shifts, sales):
    business_day = dict()

    for hour in shifts:
        if sales[hour] == 0:
            business_day[hour] = \
                sales[hour] - shifts[hour]
        else:
            business_day[hour] = \
                (shifts[hour] / sales[hour]) * 100

    return business_day


def best_and_worst_hour(percentages):
    best_hour, worst_hour = None, None

    for hour in percentages:
        p = percentages[hour]        

        if best_hour is None: 
            best_hour = hour
        if worst_hour is None: 
            worst_hour = hour

        w = percentages[worst_hour] 
        b = percentages[best_hour]
        
        # Best Hour ---
        if (p < 0) and (b < 0) and (b > p):
            best_hour = hour
        elif (p > 0) and (b > p or b < 0):
            best_hour = hour
        
        # Worst Hour ---
        if (p > 0) and (w > 0) and (w < p):
            worst_hour = hour
        elif (p < 0) and (w > p or w > 0):
            worst_hour = hour

    return best_hour, worst_hour


def main(path_to_shifts, path_to_sales):
    """
    Do not touch this function, but you can look at it, to have an idea of
    how your data should interact with each other
    """
    shifts_processed = process_shifts(path_to_shifts)
    sales_processed = process_sales(path_to_sales)
    percentages = compute_percentage(shifts_processed, sales_processed)
    best_hour, worst_hour = best_and_worst_hour(percentages)
    return best_hour, worst_hour


if __name__ == '__main__':
    path_to_sales = "./transactions.csv"
    path_to_shifts = "./work_shifts.csv"
    best_hour, worst_hour = main(path_to_shifts, path_to_sales)
    print('Best:', best_hour, '\nWorst:', worst_hour)


# Please write you name here: Owen Easter
