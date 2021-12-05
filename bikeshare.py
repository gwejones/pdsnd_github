import numpy as np
import pandas as pd
import sys
import curses
import time
import datetime
import calendar

CITY_DATA = {'Chicago': 'chicago.csv','New York City': 'new_york_city.csv','Washington': 'washington.csv'}

def read_data():
    """
    Read all bikeshare data for all cities.
    Returns:
        df - Pandas dataframe with all bikeshare data.
    """
    df = pd.DataFrame(columns = ['City'])
    for city, filename in CITY_DATA.items():
        df = df.append(pd.read_csv(filename),ignore_index=True)
        df['City'].fillna(city,inplace = True)
    df.pop('Unnamed: 0')
    df['Start Time']=pd.to_datetime(df['Start Time'])
    df['End Time']=pd.to_datetime(df['End Time'])
    return df

def about(df):
    """
    Displays info about the program and dataset.
    Args:
        df - Pandas dataframe with all bikeshare data.
    """
    print("\n" + "-"*26)
    print("US Bikeshare Data Explorer")
    print("-"*26)
    print("By: G.W.E. Jones")
    print("DataFrame Size = {}MB".format(int(df.memory_usage().sum()/1024/1024)))
    print("Number of Records = {}".format(df.shape[0]))
    return 

def draw_annotations(scr, title, modes, mode, cities_shown, city_menu, insight):
    """
    Displays annotations for data exploration page
    Args:
        scr - Curses window
        (str) title - title of page
        [str] modes - list of modes
        (int) mode - selected mode from modes
        (dict) cities_shown - boolean dict of which city to show
        [str] city_menu - menu selection for city
        (str) insight - insight to display under title
    """
    # print title line
    scr.addstr(1,curses.COLS//2-len(title)//2,title, curses.A_BOLD)
    # print insight lines
    for num, line in enumerate(insight.split('\n')):
        scr.addstr(3+num,curses.COLS//2-len(line)//2,line)
    start_col = curses.COLS//2-28  # start pos for buttons
    scr.addstr(curses.LINES-4,start_col+2,"Cities:")
    offset = 0
    for num, city in enumerate(city_menu):
        scr.addstr(curses.LINES-4,start_col+12+offset,"{})".format(num+1))
        offset += 3
        if cities_shown[city]:
            scr.addstr(curses.LINES-4,start_col+11+offset,city,curses.A_REVERSE)
        else:
            scr.addstr(curses.LINES-4,start_col+11+offset,city)
        offset += len(city) + 2
    scr.addstr(curses.LINES-2,start_col+4,"Mode:   TAB)")
    scr.addstr(curses.LINES-2,start_col+38,"m)Return to Menu")
    scr.addstr(curses.LINES-2,start_col+16,modes[mode],curses.A_REVERSE)
    scr.refresh()

def disp_travel_times(scr, df):
    """
    Displays info about the most popular travel times.
    Args:
        df - Pandas dataframe with all bikeshare data.
        scr - Curses window in which to display data.
    """
    title = "Popular Travel Times".upper()
    modes = ['Month', 'Day', 'Hour']
    cities_shown = {}
    for city in df['City'].unique():
        cities_shown[city] = True
    city_menu = [city for city in cities_shown]
    mode = 0
    key_pressed = ""
    while True:
        # Process keypresses
        if key_pressed.lower() == 'm':
            break
        try:
            if cities_shown[city_menu[int(key_pressed)-1]]:
                cities_shown[city_menu[int(key_pressed)-1]] = False
            else:
                cities_shown[city_menu[int(key_pressed)-1]] = True
        except:
            pass
        finally:
            if not any(cities_shown.values()):
                for city in cities_shown:
                    cities_shown[city]=True
        if key_pressed == '\t':
            mode = (mode+1) % len(modes)
        # Draw data visualisations
        scr.clear()
        curses.LINES, curses.COLS = scr.getmaxyx()
        city_filter = [city for city in cities_shown if cities_shown[city] == True]
        ds = df.loc[df['City'].isin(city_filter)]
        if modes[mode] == 'Month':
            ds = ds['Start Time'].dt.month.value_counts().rank()
            x_values = {ind:calendar.month_abbr[int(ind)] for ind in ds.index}
            insight = "The most common month is {}".format(calendar.month_name[int(ds.index[0])])
        elif modes[mode] == 'Day':
            ds = ds['Start Time'].dt.dayofweek.value_counts().rank()
            x_values = {ind:calendar.day_abbr[int(ind)] for ind in ds.index}
            insight = "The most common day of the week is {}".format(calendar.day_name[int(ds.index[0])])
        elif modes[mode] == 'Hour':
            ds = ds['Start Time'].dt.hour.value_counts().rank()
            x_values = {ind:" {:0>2}".format(int(ind)) for ind in ds.index}
            insight = "The most common time is the hour starting at {}".format(datetime.time(ds.index[0]).strftime("%I:00 %p"))
        s_col = curses.COLS//2-int(ds.max()//2+3)
        s_line = curses.LINES//2-int(ds.count()//2)
        scr.addstr(s_line-1,s_col-len(modes[mode])+3,modes[mode],curses.A_UNDERLINE)
        scr.addstr(s_line-1,s_col+4,"Freq",curses.A_UNDERLINE)
        for i in ds.index:
            scr.addstr(s_line+i-ds.index.min(),s_col,x_values[int(i)])
            scr.addstr(s_line+i-ds.index.min(),s_col+4, '*'*int(ds[i]))
        # Draw common screen elements
        draw_annotations(scr, title, modes, mode, cities_shown, city_menu, insight)
        key_pressed = scr.getkey()

def travel_times(df):
    curses.wrapper(disp_travel_times, df)

def disp_stations(scr, df):
    """
    Displays info about the most popular stations and routes.
    Args:
        df - Pandas dataframe with all bikeshare data.
        scr - Curses window in which to display data.
    """
    title = "Popular Stations and Routes".upper()
    modes = ['Start Station', 'End Station', 'Start -> End']
    cities_shown = {}
    for city in df['City'].unique():
        cities_shown[city] = True
    city_menu = [city for city in cities_shown]
    mode = 0
    key_pressed = ""
    while True:
        # Process keypresses
        if key_pressed.lower() == 'm':
            break
        try:
            if cities_shown[city_menu[int(key_pressed)-1]]:
                cities_shown[city_menu[int(key_pressed)-1]] = False
            else:
                cities_shown[city_menu[int(key_pressed)-1]] = True
        except:
            pass
        finally:
            if not any(cities_shown.values()):
                for city in cities_shown:
                    cities_shown[city]=True
        if key_pressed == '\t':
            mode = (mode+1) % len(modes)
        # Draw data visualisations
        scr.clear()
        curses.LINES, curses.COLS = scr.getmaxyx()
        city_filter = [city for city in cities_shown if cities_shown[city] == True]
        ds = df.loc[df['City'].isin(city_filter)]
        if modes[mode] == 'Start Station':
            ds = ds['Start Station'].value_counts().head(10)
            x_values = [item[:40] for item in ds.index] 
            insight = "The most common start station is\n" + ds.index[0]
        elif modes[mode] == 'End Station':
            ds = ds['End Station'].value_counts().head(10)
            x_values = [item[:40] for item in ds.index] 
            insight = "The most common end station is\n" + ds.index[0]
        elif modes[mode] == 'Start -> End':
            ds = ds.groupby(['Start Station','End Station']).count()['City'].sort_values(ascending = False).head(10)
            x_values = ["{} - {}".format(start, end)[:40].rstrip() for start, end in ds.index] 
            insight = "The most common route is\n" + ds.index[0][0] + " to " + ds.index[0][1]
        s_col = curses.COLS//2+12
        s_line = curses.LINES//2-int(ds.count()//2)
        for num, ind in enumerate(ds.index):
            scr.addstr(s_line+num, s_col-len(x_values[num]), x_values[num])
            scr.addstr(s_line+num, s_col+2, str(ds.iloc[num]))

        scr.addstr(s_line-1,s_col-len(modes[mode]),modes[mode],curses.A_UNDERLINE)
        scr.addstr(s_line-1,s_col+2,"Count",curses.A_UNDERLINE)
        for i in ds.index:
            pass
        # Draw common screen elements
        draw_annotations(scr, title, modes, mode, cities_shown, city_menu, insight)
        key_pressed = scr.getkey()

def stations(df):
    curses.wrapper(disp_stations, df)
    
def city_selector(df):
    """
    Prompts the user to select which cities to consider.
    Args:
        df - Pandas dataframe with all bikeshare data.
    Returns:
        [str] cities - list of cities which have been selected.
    """
    while True:
        print('\nWhich city?')
        cities = ['All']
        for city in df['City'].unique():
            cities.append(city)
        for num, city in enumerate(cities,1):
            print('{}) {}'.format(num, city))
        try:
            option = int(input('>'))
        except:
            continue
        if option == 1:
            return cities[1:]
        elif option <= len(cities) and option > 1:
            return [cities[option-1]]

def durations(df):
    """
    Show stats and raw data regarding trip duratons.
    Args:
        df - Pandas dataframe with all bikeshare data.
    """
    cities = city_selector(df)
    ds = df[df['City'].isin(cities)][['Start Time','End Time','Trip Duration']].sort_values('Trip Duration', ascending = False)
    pos = 0    # the index position in the table
    # Display stats and table
    while True:
        print('\nTravel Durations\n----------------')
        print('Cities: {}'.format(', '.join(cities)))
        print('Total travel time = {} hours'.format(ds.sum(numeric_only=True)['Trip Duration']/3600))
        print('Average trip duration = {} sec'.format(ds.mean(numeric_only=True)['Trip Duration']))
        print('Raw data:')
        print(ds.iloc[pos:pos+5])
        option = input('\n(p)revious, (n)ext, m(enu)? ')
        if option.lower()[0] == 'n':
            pos += 5
        elif option.lower()[0] == 'p':
            pos -= 5
            if pos < 0:
                pos = 0
        elif option.lower()[0] == 'm':
            break

def user_info(df):
    """
    Show stats and raw data regarding users of bikeshare.
    Args:
        df - Pandas dataframe with all bikeshare data.
    """
    cities = city_selector(df)
    ds = df[df['City'].isin(cities)][['User Type','Gender','Birth Year']]
    posn = 0    # the index position in the table
    # Display stats and table
    while True:
        print('\nUser Stats\n----------')
        print('Cities: {}'.format(', '.join(cities)))
        row_count = ds.shape[0]
        subscriber_count = ds[ds['User Type']=='Subscriber']['User Type'].count()
        customer_count = ds[ds['User Type']=='Customer']['User Type'].count()
        unk_user_count = ds['User Type'].isnull().sum()
        male_count = ds[ds['Gender']=='Male']['Gender'].count()
        female_count = ds[ds['Gender']=='Female']['Gender'].count()
        unk_gender_count = ds['Gender'].isnull().sum()
        if ds['Birth Year'].any():
            earliest_year = int(ds['Birth Year'].min())
            most_recent_year = int(ds['Birth Year'].max())
            most_common_year = int(ds['Birth Year'].mode()[0])
        else:
            earliest_year = None
            most_recent_year = None
            most_common_year = None
        print('Count for user type \'Subscriber\' = {} ({:.1f}%)'.format(customer_count,100*customer_count/row_count))
        print('Count for user type \'Customer\' = {} ({:.1f}%)'.format(subscriber_count,100*subscriber_count/row_count))
        print('Count of user with unknown type = {} ({:.1f}%)'.format(unk_user_count,100*unk_user_count/row_count))
        print('Count for gender \'Male\' = {} ({:.1f}%)'.format(male_count,100*male_count/row_count))
        print('Count for gender \'Female\' = {} ({:.1f}%)'.format(female_count,100*female_count/row_count))
        print('Count for unknown gender = {} ({:.1f}%)'.format(unk_gender_count,100*unk_gender_count/row_count))
        if earliest_year:
            print('Earliest year of birth = {}'.format(earliest_year))
        if most_recent_year:
            print('Most recent year of birth = {}'.format(most_recent_year))
        if most_common_year:
            print('Most common year of birth = {}'.format(most_common_year))
        print('Raw data:')
        print(ds.iloc[posn:posn+5])
        selection = input('\n(p)revious, (n)ext, m(enu)? ')
        if selection.lower()[0] == 'n':
            posn += 5
        elif selection.lower()[0] == 'p':
            posn -= 5
            if posn < 0:
                posn = 0
        elif selection.lower()[0] == 'm':
            break

def quit(df):
    """Exit the program."""
    print('Quitting...')
    sys.exit()

def main():
    print('Loading dataset...')
    df = read_data()
    print('Done\n')
    about(df)
    # Main Menu #
    main_menu = {'About':about,'Popular Travel Times':travel_times,'Popular Stations':stations,'Trip Duration':durations,'User Info':user_info, 'Quit':quit}
    while True:
        selections = {}
        print("\nMain Menu\n---------")
        for num, menu_item in enumerate(main_menu):
            print("{}) {}".format(num+1, menu_item))
            selections[num+1] = main_menu[menu_item] 
        try:
            selection = int(input('Enter option (number): '))
        except:
            continue
        if not (selection <= len(selections)):
            selection = len(selections)
        selections[selection](df)

if __name__ == "__main__":
    main()
