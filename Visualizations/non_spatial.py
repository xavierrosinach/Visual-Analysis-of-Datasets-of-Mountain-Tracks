import pandas as pd
import altair as alt
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# Function to create the time distribution visualizations
def time_distribution(df):

    # Start date (1st Jan of the first year), and end year (12th Dec of the last year)
    start_date = pd.to_datetime(df['date'].min()).replace(month=1, day=1)
    end_date = pd.to_datetime(df['date'].max()).replace(month=12, day=31) 

    # Create a partial dataframe
    df['date'] = pd.to_datetime(df['date'])     # Date to datetime
    all_dates = pd.date_range(start=start_date, end=end_date)     # Create a range of dates
    df_counts = df.groupby('date').size().reset_index(name='count')     # Count registers by date

    # Reindex on values to 0
    df_full = pd.DataFrame({'date': all_dates})
    df = df_full.merge(df_counts, on='date', how='left').fillna(0)

    # Create other columns
    df['month'] = df['date'].dt.strftime('%b')
    df['weekday'] = df['date'].dt.strftime('%a')
    df['year'] = df['date'].dt.year

    # Cumulative sum of counts
    df['cumul_count'] = df['count'].cumsum()

    # Selection of the year bar
    year_click = alt.selection_point(fields=['year'], on='click')

    # Year bar chart
    year_bar_chart = alt.Chart(df).mark_bar(color='#FFB84C').encode(
        x=alt.X('year:N', axis=alt.Axis(labelAngle=0), title='Year'),
        y=alt.Y('sum(count):Q', title='Total Registered Tracks'),
        opacity=alt.condition(year_click, alt.value(1), alt.value(0.2)),
        color=alt.condition(year_click, alt.value('#FFB84C'), alt.value("#818181")),
        tooltip=[(alt.Tooltip('year:N', title='Year')), (alt.Tooltip('sum(count):Q', title='Total Registered Tracks'))]
    ).add_params(year_click)

    # Month bar chart with the selected year filter
    month_bar_chart = alt.Chart(df).mark_bar(color='#F266AB').encode(
        x=alt.X('month:N', axis=alt.Axis(labelAngle=0), sort=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], title='Month'),
        y=alt.Y('sum(count):Q', title='Total Registered Tracks'),
        tooltip=[(alt.Tooltip('month:N', title='Month')), (alt.Tooltip('sum(count):Q', title='Total Registered Tracks'))]
    ).transform_filter(year_click)

    # All dates line chart
    all_dates_line = alt.Chart(df).mark_area(line=True, opacity=0.2, color='#2CD3E1').encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('cumul_count:Q', title='Cumulative Sum of Registered Tracks')
    ).add_params(year_click
    ).transform_filter(year_click)
    
    # Selection of the date with the dashed line
    selected_date = alt.selection_point(fields=['date'], on='mouseover', empty=False, nearest=True)

    # Create a dashed line for each date, used to show the date
    dashed_lines = alt.Chart(df).mark_rule(color='grey', strokeDash=[2,2]).encode(
        x=alt.X('date:T'),
        opacity=alt.condition(selected_date, alt.value(1), alt.value(0)),
        tooltip=[(alt.Tooltip('date:T', title='Date')), (alt.Tooltip('cumul_count:Q', title='Cumulative Sum of Tracks')), (alt.Tooltip('count:Q', title='Total Tracks'))]
    ).add_params(selected_date, year_click
    ).transform_filter(year_click)

    # Concatenate the two charts to create the final one of all the dates line
    all_dates_line = alt.layer(dashed_lines, all_dates_line)

    # Return all the charts
    return year_bar_chart, month_bar_chart, all_dates_line

# Comparison of the total registered tracks between two years each month
def two_years_month_comparison(df):

    # Obtain the list of sorted years
    list_years = sorted(df['year'].unique().tolist())

    # Create two dropdowns
    year1_dropdown = alt.binding_select(options=list_years, name="First year: ")
    year2_dropdown = alt.binding_select(options=list_years, name="Second year: ")

    # Create two selection points
    year_1 = alt.selection_point(fields=['year'], bind=year1_dropdown, name="Year1", value={'year':list_years[-2]})
    year_2 = alt.selection_point(fields=['year'], bind=year2_dropdown, name="Year2", value={'year':list_years[-1]})

    # Add a hover for better visualization
    hover = alt.selection_point(on="mouseover", encodings=["x"])

    # Generate the chart
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('month:N', sort=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], axis=alt.Axis(labelAngle=0), title='Month'),
        y=alt.Y('count():Q', title='Total Registered Tracks'),
        xOffset=alt.XOffset('year:N', title=None),
        color=alt.condition(hover, alt.Color('year:N', title='Year', scale=alt.Scale(range=["#F266AB", "#A459D1"])), alt.value("#818181")),
        opacity=alt.condition(hover, alt.value(1), alt.value(0.2)),
        tooltip=[(alt.Tooltip('year:N',title='Year')), (alt.Tooltip('month:N',title='Month')), (alt.Tooltip('count():Q',title='Total Registered Tracks'))]
    ).add_params(year_2, year_1, hover
    ).transform_filter((year_1 | year_2))

    # Return the chart
    return chart

# Comparison of the total registered tracks between two years each weekday
def two_years_weekday_comparison(df):

    # Obtain the list of sorted years
    list_years = sorted(df['year'].unique().tolist())

    # Create two dropdowns
    year1_dropdown = alt.binding_select(options=list_years, name="First year: ")
    year2_dropdown = alt.binding_select(options=list_years, name="Second year: ")

    # Create two selection points
    year_1 = alt.selection_point(fields=['year'], bind=year1_dropdown, name="Year1", value={'year':list_years[-2]})
    year_2 = alt.selection_point(fields=['year'], bind=year2_dropdown, name="Year2", value={'year':list_years[-1]})

    # Add a hover for better visualization
    hover = alt.selection_point(on="mouseover", encodings=["x"])

    # Generate the chart
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('weekday:N', sort=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], axis=alt.Axis(labelAngle=0), title='Day of the Week'),
        y=alt.Y('count():Q', title='Total Registered Tracks'),
        xOffset=alt.XOffset('year:N', title=None),
        color=alt.condition(hover, alt.Color('year:N', title='Year', scale=alt.Scale(range=["#F266AB", "#A459D1"])), alt.value("#818181")),
        opacity=alt.condition(hover, alt.value(1), alt.value(0.2)),
        tooltip=[(alt.Tooltip('year:N',title='Year')), (alt.Tooltip('weekday:N',title='Day of the Week')), (alt.Tooltip('count():Q',title='Total Registered Tracks'))]
    ).add_params(year_2, year_1, hover
    ).transform_filter((year_1 | year_2))

    # Return the chart
    return chart

# Sub function of difficulty info to generate all the scatter plots
def generate_difficulty_visualizations_table(df):

    # Create a color dictionary
    diff_values = ['Easy','Moderate','Difficult','Very difficult']
    diff_colors = ['#16C47F','#FFD65A','#FF9D23','#F93827']

    # Distance histogram
    dist_hist = alt.Chart(df).mark_bar().encode(
        x=alt.X('total_distance:Q', bin=True, title='Distance (km)'),
        y=alt.Y('count():Q', title='Total Registered Tracks'),
        color=alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors), legend=None),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')), (alt.Tooltip('count():Q',title='Total Registered Tracks'))]
    ).properties(width=200, height=200)

    # Distance vs time
    dist_time = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X('total_distance:Q', title='Distance (km)'),
        y=alt.Y('total_time:Q', title='Time (min)'),
        color=alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors), legend=None),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),(alt.Tooltip('total_distance:Q',title='Distance')),(alt.Tooltip('total_time:Q',title='Time'))]
    ).properties(width=200, height=200
    ).interactive()

    # Distance vs pace
    dist_pace = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X('total_distance:Q', title='Distance (km)'),
        y=alt.Y('average_pace:Q', title='Average pace (min/km)'),
        color=alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors), legend=None),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),(alt.Tooltip('total_distance:Q',title='Distance')),(alt.Tooltip('average_pace:Q',title='Pace'))]
    ).properties(width=200, height=200
    ).interactive()

    # Distance vs elevation
    dist_elev = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X('total_distance:Q', title='Distance (km)'),
        y=alt.Y('elevation_gain:Q', title='Elevation gain (meters)'),
        color=alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors), legend=None),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),(alt.Tooltip('total_distance:Q',title='Distance')),(alt.Tooltip('elevation_gain:Q',title='Elevation'))]
    ).properties(width=200, height=200
    ).interactive()

    # Time vs distance
    time_dist = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X('total_time:Q', title='Time (min)'),
        y=alt.Y('total_distance:Q', title='Distance (km)'),
        color=alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors), legend=None),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),(alt.Tooltip('total_time:Q',title='Time')),(alt.Tooltip('total_distance:Q',title='Distance'))]
    ).properties(width=200, height=200
    ).interactive()

    # Time histogram
    time_hist = alt.Chart(df).mark_bar().encode(
        x=alt.X('total_time:Q', bin=True, title='Time (min)'),
        y=alt.Y('count():Q', title='Total Registered Tracks'),
        color=alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors), legend=None),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')), (alt.Tooltip('count():Q',title='Total Registered Tracks'))]
    ).properties(width=200, height=200)

    # Time vs pace
    time_pace = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X('total_time:Q', title='Time (min)'),
        y=alt.Y('average_pace:Q', title='Average pace (min/km)'),
        color=alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors), legend=None),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),(alt.Tooltip('total_time:Q',title='Time')),(alt.Tooltip('average_pace:Q',title='Pace'))]
    ).properties(width=200, height=200
    ).interactive()

    # Time vs elevation
    time_elev = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X('total_time:Q', title='Time (min)'),
        y=alt.Y('elevation_gain:Q', title='Elevation gain (meters)'),
        color=alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors), legend=None),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),(alt.Tooltip('total_time:Q',title='Time')),(alt.Tooltip('elevation_gain:Q',title='Elevation'))]
    ).properties(width=200, height=200
    ).interactive()

    # Pace vs distance
    pace_dist = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X('average_pace:Q', title='Average pace (min/km)'),
        y=alt.Y('total_distance:Q', title='Distance (km)'),
        color=alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors), legend=None),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),(alt.Tooltip('average_pace:Q',title='Pace')),(alt.Tooltip('total_distance:Q',title='Distance'))]
    ).properties(width=200, height=200
    ).interactive()

    # Pace vs time
    pace_time = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X('average_pace:Q', title='Average pace (min/km)'),
        y=alt.Y('total_time:Q', title='Time (min)'),
        color=alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors), legend=None),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),(alt.Tooltip('average_pace:Q',title='Pace')),(alt.Tooltip('total_time:Q',title='Time'))]
    ).properties(width=200, height=200
    ).interactive()

    # Pace histogram
    pace_hist = alt.Chart(df).mark_bar().encode(
        x=alt.X('average_pace:Q', bin=True, title='Average pace (min/km)'),
        y=alt.Y('count():Q', title='Total Registered Tracks'),
        color=alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors), legend=None),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')), (alt.Tooltip('count():Q',title='Total Registered Tracks'))]
    ).properties(width=200, height=200)

    # Pace vs elevation
    pace_elev = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X('average_pace:Q', title='Average pace (min/km)'),
        y=alt.Y('elevation_gain:Q', title='Elevation gain (meters)'),
        color=alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors), legend=None),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),(alt.Tooltip('average_pace:Q',title='Pace')),(alt.Tooltip('elevation_gain:Q',title='Elevation'))]
    ).properties(width=200, height=200
    ).interactive()

    # Elevation vs distance
    elev_dist = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X('elevation_gain:Q', title='Elevation gain (meters)'),
        y=alt.Y('total_distance:Q', title='Distance (km)'),
        color=alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors), legend=None),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),(alt.Tooltip('elevation_gain:Q',title='Elevation')),(alt.Tooltip('total_distance:Q',title='Distance'))]
    ).properties(width=200, height=200
    ).interactive()

    # Elevation vs time
    elev_time = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X('elevation_gain:Q', title='Elevation gain (meters)'),
        y=alt.Y('total_time:Q', title='Time (min)'),
        color=alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors), legend=None),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),(alt.Tooltip('elevation_gain:Q',title='Elevation')),(alt.Tooltip('total_time:Q',title='Time'))]
    ).properties(width=200, height=200
    ).interactive()

    # Elevation vs pace
    elev_pace = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X('elevation_gain:Q', title='Elevation gain (meters)'),
        y=alt.Y('average_pace:Q', title='Average pace (min/km)'),
        color=alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors), legend=None),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),(alt.Tooltip('elevation_gain:Q',title='Elevation')),(alt.Tooltip('average_pace:Q',title='Pace'))]
    ).properties(width=200, height=200
    ).interactive()

    # Elevation histogram
    elev_hist = alt.Chart(df).mark_bar().encode(
        x=alt.X('elevation_gain:Q', bin=True, title='Elevation gain (meters)'),
        y=alt.Y('count():Q', title='Total Registered Tracks'),
        color=alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors), legend=None),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')), (alt.Tooltip('count():Q',title='Total Registered Tracks'))]
    ).properties(width=200, height=200)

    # Horizontal distribution of each row
    dist_row = alt.hconcat(dist_hist, dist_time, dist_pace, dist_elev)
    time_row = alt.hconcat(time_dist, time_hist, time_pace, time_elev)
    pace_row = alt.hconcat(pace_dist, pace_time, pace_hist, pace_elev)
    elev_row = alt.hconcat(elev_dist, elev_time, elev_pace, elev_hist)

    # Final visualitzation
    return alt.vconcat(dist_row, time_row, pace_row, elev_row)

# Sub function of difficulty info to generate lines from min to max
def generate_min_max_lines(df, bar_selection):

    # Create a color dictionary
    diff_values = ['Easy','Moderate','Difficult','Very difficult']
    diff_colors = ['#16C47F','#FFD65A','#FF9D23','#F93827']

    # Distance lines
    dist_line = alt.Chart(df).mark_line().encode(
        x=alt.X('min(total_distance):Q', title='Distance (km)'),
        x2=alt.X2('max(total_distance):Q'),
        y=alt.Y('difficulty:N', title='Difficulty', sort=['Easy','Moderate','Difficult','Very difficult']))

    # Distance mean points
    dist_mean_point = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X('mean(total_distance):Q', title='Distance (km)'),
        y=alt.Y('difficulty:N', title='Difficulty', sort=['Easy','Moderate','Difficult','Very difficult']))

    # Distance final visualization
    dist_min_max = alt.layer(dist_line, dist_mean_point).encode(
        color=alt.condition(bar_selection, alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors)), alt.value("#818181")),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),  (alt.Tooltip('min(total_distance):Q', title='Min distance')), (alt.Tooltip('max(total_distance):Q', title='Max distance')), (alt.Tooltip('mean(total_distance):Q', title='Average distance', format='.2f'))],
        opacity=alt.condition(bar_selection, alt.value(1), alt.value(0.4))
    ).add_params(bar_selection
    ).properties(width=300, height=75, title='Distance range plot')

    # Time lines
    time_line = alt.Chart(df).mark_line().encode(
        x=alt.X('min(total_time):Q', title='Time (min)'),
        x2=alt.X2('max(total_time):Q'),
        y=alt.Y('difficulty:N', title='Difficulty', sort=['Easy','Moderate','Difficult','Very difficult']))

    # Time mean points
    time_mean_point = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X('mean(total_time):Q', title='Time (min)'),
        y=alt.Y('difficulty:N', title='Difficulty', sort=['Easy','Moderate','Difficult','Very difficult']))

    # Time visualization
    time_min_max = alt.layer(time_line, time_mean_point).encode(
        color=alt.condition(bar_selection, alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors)), alt.value("#818181")),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),  (alt.Tooltip('min(total_time):Q', title='Min time')), (alt.Tooltip('max(total_time):Q', title='Max time')), (alt.Tooltip('mean(total_time):Q', title='Average time', format='.2f'))],
        opacity=alt.condition(bar_selection, alt.value(1), alt.value(0.4))
    ).add_params(bar_selection
    ).properties(width=300, height=75, title='Time range plot')

    # Pace lines
    pace_line = alt.Chart(df).mark_line().encode(
        x=alt.X('min(average_pace):Q', title='Pace (min/km)'),
        x2=alt.X2('max(average_pace):Q'),
        y=alt.Y('difficulty:N', title='Difficulty', sort=['Easy','Moderate','Difficult','Very difficult']))

    # Pace mean points
    pace_mean_point = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X('mean(average_pace):Q', title='Pace (min/km)'),
        y=alt.Y('difficulty:N', title='Difficulty', sort=['Easy','Moderate','Difficult','Very difficult']))

    # Pace visualization
    pace_min_max = alt.layer(pace_line, pace_mean_point).encode(
        color=alt.condition(bar_selection, alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors)), alt.value("#818181")),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),  (alt.Tooltip('min(average_pace):Q', title='Min pace')), (alt.Tooltip('max(average_pace):Q', title='Max pace')), (alt.Tooltip('mean(average_pace):Q', title='Average pace', format='.2f'))],
        opacity=alt.condition(bar_selection, alt.value(1), alt.value(0.4))
    ).add_params(bar_selection
    ).properties(width=300, height=75, title='Average pace range plot')

    # Elevation lines
    elev_line = alt.Chart(df).mark_line().encode(
        x=alt.X('min(elevation_gain):Q', title='Elevation (m)'),
        x2=alt.X2('max(elevation_gain):Q'),
        y=alt.Y('difficulty:N', title='Difficulty', sort=['Easy','Moderate','Difficult','Very difficult']))

    # Elevation mean points
    elev_mean_point = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X('mean(elevation_gain):Q', title='Elevation (m)'),
        y=alt.Y('difficulty:N', title='Difficulty', sort=['Easy','Moderate','Difficult','Very difficult']))

    # Elevation visualization
    elev_min_max = alt.layer(elev_line, elev_mean_point).encode(
        color=alt.condition(bar_selection, alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors)), alt.value("#818181")),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),  (alt.Tooltip('min(elevation_gain):Q', title='Min elevation')), (alt.Tooltip('max(elevation_gain):Q', title='Max elevation')), (alt.Tooltip('mean(elevation_gain):Q', title='Average elevation', format='.2f'))],
        opacity=alt.condition(bar_selection, alt.value(1), alt.value(0.4))
    ).add_params(bar_selection
    ).properties(width=300, height=75, title='Elevation gain range plot')

    # Return all the paths in vertical disposition
    return alt.vconcat(dist_min_max, time_min_max, pace_min_max, elev_min_max)

# Plots de difficulty information - different quantitative variables information
def difficulty_info(df):

    # Select only desired columns of the dataframe
    df = df[['difficulty','total_distance','total_time','average_pace','elevation_gain']].copy()

    # Replace values to english
    df['difficulty'] = df['difficulty'].replace({'Fàcil': 'Easy',
                                                'Moderat': 'Moderate',
                                                'Difícil': 'Difficult',
                                                'Molt difícil': 'Very difficult',
                                                'Només experts': 'Very difficult'})

    # Create a color dictionary
    diff_values = ['Easy','Moderate','Difficult','Very difficult']
    diff_colors = ['#16C47F','#FFD65A','#FF9D23','#F93827']

    # Selection point for the bars of difficulty
    bar_selection = alt.selection_point(fields=['difficulty'])

    # Difficulty with bars
    difficulty_bars = alt.Chart(df).mark_bar().encode(
        x=alt.X('difficulty:N', title='Difficulty', sort=diff_values, axis=alt.Axis(labelAngle=0)), 
        y=alt.Y('count():Q', title='Total Registered Tracks'),
        color=alt.condition(bar_selection, alt.Color('difficulty:N', title='Difficulty', scale=alt.Scale(domain=diff_values, range=diff_colors)), alt.value("#818181")),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),  (alt.Tooltip('count():Q', title='Total Registered Tracks'))],
        opacity=alt.condition(bar_selection, alt.value(1), alt.value(0.4))
    ).add_params(bar_selection)

    # Create the min_max lines for the four variables
    min_max_lines = generate_min_max_lines(df, bar_selection)

    # Create the charts grid
    scatter_grid = generate_difficulty_visualizations_table(df)

    # Add the parameters and filter
    scatter_grid = scatter_grid.transform_filter(bar_selection)

    return difficulty_bars, min_max_lines, scatter_grid

# Different charts to create the calendar
def calendar_weather(df, weather_df):

    # Create a color dictionary
    weather_vals = ['Clear','Cloudy','Drizzle','Rain','Snow']
    weather_colors = ['#E6AC00',"#878F97","#74BAE6","#006AFF","#B29FEA"]

    # Emojis dict
    emojis_dict = {'Rain':'🌧️', 'Drizzle':'🌦️', 'Clear':'☀️', 'Snow':'❄️', 'Cloudy':'☁️'}

    # Apply the emoji
    weather_df['weather_emoji'] = weather_df['weather_condition'].map(emojis_dict)

    # New temporal data
    weather_df['date'] = pd.to_datetime(weather_df['date'])
    weather_df['year'] = weather_df['date'].dt.year
    weather_df['month'] = weather_df['date'].dt.month_name().str[:3]
    weather_df['weekday'] = weather_df['date'].dt.day_name().str[:3]
    weather_df['week_num'] = weather_df['date'].dt.strftime('%W').astype(int)

    # Create the column 'mean_temp'
    weather_df['mean_temp'] = round((weather_df['max_temp'] + weather_df['min_temp'])/2, 2)

    # Obtain a dataframe with the counts of all dates
    date_counts = df.groupby('date').size().reset_index(name='total_tracks')
    date_counts['date'] = pd.to_datetime(date_counts['date'])

    # Merge it with the weather dataframe
    weather_df = weather_df.merge(date_counts, on='date', how='left')
    weather_df['total_tracks'] = weather_df['total_tracks'].fillna(0).astype(int)

    # Weather selector for the pie chart
    weather_selection = alt.selection_point(fields=['weather_condition'], on='click')

    # Create a years dropdown
    year_dropdown = alt.binding_select(options=weather_df['year'].unique().tolist(), name="Select a year: ")
    year_selection = alt.selection_point(fields=['year'], bind=year_dropdown, value={'year':weather_df['year'].max()})

    # Boolean selection to show the weather conditions
    weather_checkbox = alt.binding_checkbox(name="Show weather conditions: ")
    checkbox_selection = alt.param(bind=weather_checkbox)

    # Donut chart with the total charts per weather condition
    pie_chart = alt.Chart(weather_df).mark_arc(innerRadius=30, stroke='white').encode(
        theta=alt.Theta('sum(total_tracks):Q'),
        color=alt.Color('weather_condition:N', title='Weather Condition', scale=alt.Scale(domain=weather_vals, range=weather_colors)),
        opacity=alt.condition(weather_selection, alt.value(1), alt.value(0.2)),
        tooltip=[(alt.Tooltip('weather_condition:N', title='Weather Condition')), (alt.Tooltip('sum(total_tracks):Q', title='Total Tracks'))]
    ).add_params(year_selection, weather_selection
    ).transform_filter(year_selection)

    # Mean temperature and tracks scatter plot
    scatter_plot = alt.Chart(weather_df).mark_point(filled=True, fillOpacity=1).encode(
        x=alt.X('mean_temp:Q', title='Mean Temperature'),
        y=alt.Y('total_tracks:Q', title='Total Registered Tracks'),
        color=alt.Color('weather_condition:N', title='Weather Condition', scale=alt.Scale(domain=weather_vals, range=weather_colors)),
        opacity=alt.condition((weather_selection & year_selection), alt.value(1), alt.value(0)),
        tooltip=[(alt.Tooltip('weather_condition:N', title='Weather Condition')), (alt.Tooltip('total_tracks:Q', title='Total Tracks')), (alt.Tooltip('mean_temp:Q', title='Mean temperature'))]
    ).interactive(
    ).add_params(year_selection, weather_selection
    ).transform_filter(((alt.datum.total_tracks > 0) & year_selection))

    # Background calendar heat map
    background_color = alt.Chart(weather_df).mark_rect(stroke='white').encode(
        x=alt.X('week_num:O', axis=None),
        y=alt.Y('weekday:N', sort=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], title='Day of the Week'),
        color=alt.condition(weather_selection, alt.Color('sum(total_tracks):Q', scale=alt.Scale(range=['#ffffff', '#2B4F81']), legend=alt.Legend(title='Total Registered Tracks')), alt.value("#818181")),
        tooltip=[(alt.Tooltip('date:T', title='Date')), (alt.Tooltip('weather_condition:N', title='Weather Condition')), (alt.Tooltip('sum(total_tracks):Q', title='Total Registered Tracks'))])

    # Emoji with the weather condition
    emoji = alt.Chart(weather_df).mark_text().encode(
        x=alt.X('week_num:O', axis=None),
        y=alt.Y('weekday:N', sort=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], title='Day of the Week'),
        text=alt.Text('weather_emoji:N'),
        opacity=alt.condition(checkbox_selection, alt.value(1), alt.value(0))
    ).add_params(checkbox_selection)

    # Final calendar chart
    calendar = alt.layer(background_color, emoji).encode(
        opacity=alt.condition(weather_selection, alt.value(1), alt.value(0.4))
    ).add_params(year_selection, weather_selection
    ).transform_filter(year_selection)

    return pie_chart, scatter_plot, calendar

# Given a single track dataframe, generates the elevation profile
def elevation_profile_and_pace_bars(full_track_df, track_km_df):

    # Add the zero column for the first value on the y axis
    track_km_df['zero'] = 0

    # Create the row km
    full_track_df['km'] = full_track_df['elap_dist'].astype(int)

    # Dictionaries with the colors of the groups
    pace_color_dict = {'Less than 15 min/km':'#AC1754', 'From 15 to 30 min/km':'#E53888', 'From 30 to 45 min/km':'#F37199', 'More than 45 min/km':'#F7A8C4'}

    # Merge it with the km df to obtain the average pace
    track_km_df_part = track_km_df[['km', 'avg_pace', 'elev_gain', 'uphill_perc']]
    full_track_df = full_track_df.merge(track_km_df_part, on='km')

    # Create the elevation profile
    elevation_profile = alt.Chart(full_track_df).mark_line(color='#4CCD99').encode(
        x=alt.X('elap_dist:Q', title='Distance'),
        y=alt.Y('elev:Q', title='Elevation'))
    
    # Pace bars
    pace_bars = alt.Chart(track_km_df).mark_bar(stroke='white').encode(
        x=alt.X('km:Q'),
        x2=alt.X2('next_km:Q'),
        y=alt.Y('avg_pace:Q', title='Average Pace'),
        y2=alt.Y2('zero:Q', title=None),
        color=alt.Color('pace_group:O',
                        title='Pace group', 
                        scale=alt.Scale(domain=list(pace_color_dict.keys()), range=list(pace_color_dict.values()))))

    # Selection of the distance with the dashed line
    selected_dist = alt.selection_point(fields=['elap_dist'], on='mouseover', empty=False, nearest=True)

    # Dashed lines with the tooltip
    dashed_lines = alt.Chart(full_track_df).mark_rule(color='grey', strokeDash=[2, 2]).encode(
        x=alt.X('elap_dist:Q'),
        opacity=alt.condition(selected_dist, alt.value(1), alt.value(0)),
        tooltip=[(alt.Tooltip('elap_dist:Q', title='Distance')), (alt.Tooltip('elev:Q', title='Elevation Gain')), (alt.Tooltip('km:Q', title='Kilometer')), (alt.Tooltip('avg_pace:Q', title='Km Average Pace')), (alt.Tooltip('elev_gain:Q', title='Km Elevation Gain')), (alt.Tooltip('uphill_perc:Q', title='Km Uphill Percentage'))]
    ).add_params(selected_dist)

    # Combination of the charts
    final_chart = alt.layer(alt.layer(pace_bars, dashed_lines), elevation_profile).encode(
        x=alt.X(scale=alt.Scale(domain=[0, full_track_df['elap_dist'].iloc[-1]]))
    ).resolve_scale(y='independent')

    return final_chart