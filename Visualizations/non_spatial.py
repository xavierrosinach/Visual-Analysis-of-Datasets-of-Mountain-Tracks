import os
import pandas as pd
import altair as alt
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# Function to create the time distribution number 1
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
    year_bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('sum(count):Q', title='Total Registered Tracks'),
        y=alt.Y('year:N', title='Year'),
        opacity=alt.condition(year_click, alt.value(1), alt.value(0.2)),
        tooltip=[(alt.Tooltip('year:N', title='Year')), (alt.Tooltip('sum(count):Q', title='Total Registered Tracks'))]
    ).add_params(year_click
    ).properties(height=400, width=350, title='Total Registered Tracks per Year')

    # Month bar chart with the selected year filter
    month_bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('sum(count):Q', title='Total Registered Tracks'),
        y=alt.Y('month:N', sort=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], title='Month'),
        tooltip=[(alt.Tooltip('month:N', title='Month')), (alt.Tooltip('sum(count):Q', title='Total Registered Tracks'))]
    # ).add_params(year_click
    ).transform_filter(year_click
    ).properties(height=400, width=350, title='Total Registered Tracks per Month')
                    
    # All dates line chart
    all_dates_line = alt.Chart(df).mark_area(line=True, opacity=0.2).encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('cumul_count:Q', title='Cumulative Sum of Registered Tracks')
    ).add_params(year_click
    ).transform_filter(year_click
    ).properties(height=400, width=800, title='Evolution of Registered Tracks trough the years')

    # Selection of the date with the dashed line
    selected_date = alt.selection_point(fields=['date'], on='mouseover', empty=False, nearest=True)

    # Create a dashed line for each date, used to show the date
    dashed_lines = alt.Chart(df).mark_rule(color='grey', strokeDash=[2,2]).encode(
        x=alt.X('date:T'),
        opacity=alt.condition(selected_date, alt.value(1), alt.value(0)),
        tooltip=[(alt.Tooltip('date:T', title='Date')), (alt.Tooltip('cumul_count:Q', title='Cumulative Sum of Tracks')), (alt.Tooltip('count:Q', title='Total Tracks'))]
    ).add_params(selected_date, year_click
    ).transform_filter(year_click)

    # Full disposition
    final_chart = alt.vconcat(alt.hconcat(year_bar_chart, month_bar_chart), alt.layer(dashed_lines, all_dates_line))

    # Return the chart
    return final_chart

# Obtain the two charts
def two_years_comparisons(df, year1, year2):

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
    df['date_no_year'] = df['date'].dt.strftime('%m-%d')  # Only month and year

    # Filter the dataframe
    df = df[(df['year'] == year1) | (df['year'] == year2)]

    # Months comparison
    months_comparison = alt.Chart(df).mark_bar().encode(
        x=alt.X('month:N', sort=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], axis=alt.Axis(labelAngle=0), title='Month'),
        y=alt.Y('sum(count):Q', title='Total Registered Tracks'),
        xOffset=alt.XOffset('year:N', title=None),
        color=alt.Color('year:N', title='Year'),
        tooltip=[(alt.Tooltip('year:N',title='Year')), (alt.Tooltip('month:N',title='Month')), (alt.Tooltip('sum(count):Q',title='Total Registered Tracks'))]
    ).properties(width=800, height=400, title=f'Comparison of Total Registered Tracks each month between {year1} and {year2}')

    # Weekdays comparison
    weekdays_comparison = alt.Chart(df).mark_bar().encode(
        x=alt.X('weekday:N', sort=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], axis=alt.Axis(labelAngle=0), title='Weekday'),
        y=alt.Y('sum(count):Q', title='Total Registered Tracks'),
        xOffset=alt.XOffset('year:N', title=None),
        color=alt.Color('year:N', title='Year'),
        tooltip=[(alt.Tooltip('year:N',title='Year')), (alt.Tooltip('weekday:N',title='Day of the Week')), (alt.Tooltip('sum(count):Q',title='Total Registered Tracks'))]
    ).properties(width=800, height=400, title=f'Comparison of Total Registered Tracks each weekday between {year1} and {year2}')

    return months_comparison, weekdays_comparison

# Returns a calendar with weather information
def calendar_weather(df, year, month):

    # Cut the dataframe with the year and the month
    month_df = df[(df['year'] == year) & (df['month'] == month)].copy()
    month_df['week_number'] = pd.to_datetime(month_df['date']).dt.isocalendar().week    	# Insert the week number to create the calendar

    # Weather click selection to get an impresion of the type of weathers
    weather_click = alt.selection_point(fields=['weather_condition'], on='click')

    # Creation of the pie chart
    pie_chart = alt.Chart(month_df).mark_arc(innerRadius = 50, stroke='white').encode(
        color=alt.Color('weather_condition:N', title='Weather Condition'),
        theta=alt.Theta('count():Q'),
        opacity=alt.condition(weather_click, alt.value(1), alt.value(0.4)),
        tooltip=[(alt.Tooltip('weather_condition:N', title='Weather Condition')), (alt.Tooltip('count():Q', title='Total Registered Tracks'))]
    ).add_params(weather_click
    ).properties(width=250, height=250, title='Weather Condition Distribution')

    # Hover Selection
    hover = alt.selection_point(on='mouseover', nearest=True, fields=['date'], empty=False)

    # Calendar Chart
    calendar = alt.Chart(month_df).mark_point(filled=True, stroke='white').encode(
        x=alt.X('weekday:N', axis=alt.Axis(labelAngle=0, orient='top'), 
                sort=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], title=None),
        y=alt.Y('week_number:O', axis=None),
        size=alt.condition(hover, alt.SizeValue(3000), alt.Size('count():Q', scale=alt.Scale(range=[0, 2500]))),
        color=alt.Color('weather_condition:N', title='Weather Condition'),
        opacity=alt.condition(weather_click, alt.value(1), alt.value(0.4)),
        tooltip=[alt.Tooltip('date:T', title='Date'), 
                 alt.Tooltip('count():Q', title='Total Registered Tracks'),
                 alt.Tooltip('weather_condition:N', title='Weather Condition'), 
                 alt.Tooltip('min_temp:Q', title='Minimum Temperature'), 
                 alt.Tooltip('max_temp:Q', title='Maximum Temperature')]
    ).add_params(weather_click, hover
    ).properties(width=600, height=600, title='Total Registered Tracks per Day')

    # Minimum point
    min_point = alt.Chart(month_df).mark_point(filled=True).encode(
        x=alt.X('date:T'),
        y=alt.Y('min(min_temp):Q'))

    # Maximum point
    max_point = alt.Chart(month_df).mark_point(filled=True).encode(
        x=alt.X('date:T'),
        y=alt.Y('max(max_temp):Q'))

    # Vertical lines from minimum to maximum
    lines = alt.Chart(month_df).mark_line().encode(
        x=alt.X('date:T'),
        y=alt.Y('min(min_temp):Q'),
        y2=alt.Y2('max(max_temp):Q'),
        size=alt.condition(hover, alt.value(3), alt.value(1))
    ).add_params(hover)

    # Full temperatures evolution chart
    temp_evo = alt.layer(lines, min_point, max_point).encode(
        x=alt.X(title='Date'),
        y=alt.Y(title='Temperature Range'),
        color=alt.Color('weather_condition:N', title='Weather Condition'),
        tooltip=[(alt.Tooltip('date:T', title='Date')),
                (alt.Tooltip('weather_condition:N', title='Weather Condition')), 
                (alt.Tooltip('min_temp:Q', title='Minimum Temperature')), 
                (alt.Tooltip('max_temp:Q', title='Maximum Temperature'))],
        opacity=alt.condition(weather_click, alt.value(1), alt.value(0.4)),
    ).add_params(weather_click
    ).properties(width=250, height=250, title='Temperatures Evolution')

    # Create the final dataframe and return it
    final_chart = alt.hconcat(alt.vconcat(pie_chart, temp_evo), calendar)
    return final_chart

# Plot the difficulty bar chart and a scatter plot with the defined axis
def difficulty_scatter(df, x_axis, y_axis):

    # For each type, define a type
    axis_title_dict = {'total_time':'Total Time', 'total_distance':'Total Distance', 'average_speed':'Average Speed', 'average_pace':'Average Pace', 'elevation_gain':'Elevation Gain'}
    x_axis_title = axis_title_dict[x_axis]
    y_axis_title = axis_title_dict[y_axis]

    # Selection point for the bars of difficulty
    bar_selection = alt.selection_point(fields=['difficulty'])

    # Difficulty with bars
    difficulty_bars = alt.Chart(df).mark_bar().encode(
        x=alt.X('difficulty:N', title='Difficulty', sort=['Fàcil','Moderat','Difícil','Molt difícil'], axis=alt.Axis(labelAngle=0)), 
        y=alt.Y('count():Q', title='Total Registered Tracks'),
        color=alt.Color('difficulty:N', title='Difficulty'),
        tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),  (alt.Tooltip('count():Q', title='Total Registered Tracks'))],
        opacity=alt.condition(bar_selection, alt.value(1), alt.value(0.4))
    ).add_params(bar_selection
    ).properties(width=400, height=200, title='Difficulty of Tracks Distribution')

    # Hover to highlight
    hover = alt.selection_point(on='mouseover', fields=['total_distance','total_time'], empty=False)

    # Scatter plot filtered by interval
    scatter_plot = alt.Chart(df).mark_point(filled=True, fillOpacity=1).encode(
        x=alt.X(f'{x_axis}:Q', title=x_axis_title),
        y=alt.Y(f'{y_axis}:Q', title=y_axis_title),
        color=alt.Color('difficulty:N', title='Difficulty'),
        tooltip=[(alt.Tooltip('track_id', title='Track Identifier')),
                (alt.Tooltip('difficulty:N', title='Difficulty')),
                (alt.Tooltip('total_distance:Q', title='Distance')),
                (alt.Tooltip('total_time:Q', title='Time')),
                (alt.Tooltip('average_speed:Q', title='Average Speed')),
                (alt.Tooltip('average_pace:Q', title='Average Pace')),
                (alt.Tooltip('elevation_gain:Q', title='Elevation Gain'))],
        size=alt.condition(hover, alt.value(100), alt.value(20))
    ).add_params(hover
    ).transform_filter(bar_selection
    ).properties(width=500, height=500, title='Tracks of the zone'
    ).interactive()

    # Add a hover to highlight the line
    x_hover = alt.selection_point(on='mouseover', fields=['difficulty'], empty=False)

    # Point for the x-axis distribution
    point_x = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X(f'mean({x_axis}):Q'),
        y=alt.Y('difficulty:N', sort=['Fàcil','Moderat','Difícil','Molt difícil']),
        color=alt.Color('difficulty:N', legend=None))

    # All points of the x axis, depending on the hover on the scatterplot
    all_points_x = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X(f'{x_axis}:Q'),
        y=alt.Y('difficulty:N', sort=['Fàcil','Moderat','Difícil','Molt difícil']),
        color=alt.Color('difficulty:N', legend=None)
    ).transform_filter(hover)

    # Line for the x-axis distribution
    line_x = alt.Chart(df).mark_line().encode(
        x=alt.X(f'min({x_axis}):Q'),
        x2=alt.X2(f'max({x_axis}):Q'),
        y=alt.Y('difficulty:N', sort=['Fàcil','Moderat','Difícil','Molt difícil']),
        color=alt.Color('difficulty:N', legend=None),
        size=alt.condition(x_hover, alt.value(3), alt.value(1))
    ).add_params(x_hover)

    # X Axis distribution
    x_axis_dist = alt.layer(line_x, point_x, all_points_x).encode(
            x=alt.X(title=x_axis_title),
            y=alt.Y(title='Difficulty'),
            opacity=alt.condition(bar_selection, alt.value(1), alt.value(0.4)),
            tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),
                    (alt.Tooltip(f'mean({x_axis}):Q', title='Mean Value', format=".2f")),
                    (alt.Tooltip(f'min({x_axis}):Q', title='Min Value')),
                    (alt.Tooltip(f'max({x_axis}):Q', title='Max Value'))]
    ).add_params(bar_selection
    ).properties(width=400, height=75, title=f'{x_axis_title} - Difficulty Intervals')

    # Add a hover to highlight the line
    y_hover = alt.selection_point(on='mouseover', fields=['difficulty'], empty=False)

    # Point for the y-axis distribution
    point_y = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X(f'mean({y_axis}):Q'),
        y=alt.Y('difficulty:N', sort=['Fàcil','Moderat','Difícil','Molt difícil']),
        color=alt.Color('difficulty:N', legend=None))

    # Line for the y-axis distribution
    line_y = alt.Chart(df).mark_line().encode(
        x=alt.X(f'min({y_axis}):Q'),
        x2=alt.X2(f'max({y_axis}):Q'),
        y=alt.Y('difficulty:N', sort=['Fàcil','Moderat','Difícil','Molt difícil']),
        color=alt.Color('difficulty:N', legend=None),
        size=alt.condition(y_hover, alt.value(3), alt.value(1))
    ).add_params(y_hover)

    # All points of the y axis, depending on the hover on the scatterplot
    all_points_y = alt.Chart(df).mark_point(filled=True).encode(
        x=alt.X(f'{y_axis}:Q'),
        y=alt.Y('difficulty:N', sort=['Fàcil','Moderat','Difícil','Molt difícil']),
        color=alt.Color('difficulty:N', legend=None)
    ).transform_filter(hover)

    # Y Axis distribution
    y_axis_dist = alt.layer(line_y, point_y, all_points_y).encode(
            x=alt.X(title=y_axis_title),
            y=alt.Y(title='Difficulty'),
            opacity=alt.condition(bar_selection, alt.value(1), alt.value(0.4)),
            tooltip=[(alt.Tooltip('difficulty:N', title='Difficulty')),
                    (alt.Tooltip(f'mean({x_axis}):Q', title='Mean Value', format=".2f")),
                    (alt.Tooltip(f'min({x_axis}):Q', title='Min Value')),
                    (alt.Tooltip(f'max({x_axis}):Q', title='Max Value'))]
    ).add_params(bar_selection
    ).properties(width=400, height=75, title=f'{y_axis_title} - Difficulty Intervals')

    # Distribute the final chart
    final_chart = alt.hconcat(alt.vconcat(difficulty_bars, x_axis_dist, y_axis_dist), scatter_plot)
    return final_chart

# All quantitative variables histograms with filter
def all_quantitative_histograms(df):

    # X Axis brush to select data
    brush = alt.selection_interval(encodings=['x'])

    # Distance histogram background
    distance_back = alt.Chart(df).mark_bar(opacity=0.4).encode(
        x=alt.X('total_distance:Q', bin=True, title='Total Distance'),
        y=alt.Y('count():Q'),
        tooltip=[(alt.Tooltip('count():Q', title='Total Registered Tracks'))])

    # Distance histogram
    distance = alt.Chart(df).mark_bar().encode(
        x=alt.X('total_distance:Q', bin=True, title='Total Distance'),
        y=alt.Y('count():Q'),
        tooltip=[(alt.Tooltip('count():Q', title='Total Filtered Tracks'))]
    ).transform_filter(brush)

    # Final
    final_distance = alt.layer(distance_back, distance).add_params(brush
                ).properties(width=300, height=300, title='Total Distance Distribution of Registered Tracks')

    # Time histogram background
    time_back = alt.Chart(df).mark_bar(opacity=0.4).encode(
        x=alt.X('total_time:Q', bin=True, title='Total Time'),
        y=alt.Y('count():Q'),
        tooltip=[(alt.Tooltip('count():Q', title='Total Registered Tracks'))])

    # Time histogram
    time = alt.Chart(df).mark_bar().encode(
        x=alt.X('total_time:Q', bin=True, title='Total Time'),
        y=alt.Y('count():Q'),
        tooltip=[(alt.Tooltip('count():Q', title='Total Filtered Tracks'))]
    ).transform_filter(brush)

    # Final
    final_time = alt.layer(time_back, time).add_params(brush
                ).properties(width=300, height=300, title='Total Time Distribution of Registered Tracks')

    # Time histogram background
    pace_back = alt.Chart(df).mark_bar(opacity=0.4).encode(
        x=alt.X('average_pace:Q', bin=True, title='Average Pace'),
        y=alt.Y('count():Q'),
        tooltip=[(alt.Tooltip('count():Q', title='Total Registered Tracks'))])

    # Time histogram
    pace = alt.Chart(df).mark_bar().encode(
        x=alt.X('average_pace:Q', bin=True, title='Average Pace'),
        y=alt.Y('count():Q'),
        tooltip=[(alt.Tooltip('count():Q', title='Total Filtered Tracks'))]
    ).transform_filter(brush)

    # Final
    final_pace = alt.layer(pace_back, pace).add_params(brush
                ).properties(width=300, height=300, title='Average Pace Distribution of Registered Tracks')

    # Time histogram background
    elevation_back = alt.Chart(df).mark_bar(opacity=0.4).encode(
        x=alt.X('elevation_gain:Q', bin=True, title='Elevation Gain'),
        y=alt.Y('count():Q'),
        tooltip=[(alt.Tooltip('count():Q', title='Total Registered Tracks'))])

    # Time histogram
    elevation = alt.Chart(df).mark_bar().encode(
        x=alt.X('elevation_gain:Q', bin=True, title='Elevation Gain'),
        y=alt.Y('count():Q'),
        tooltip=[(alt.Tooltip('count():Q', title='Total Filtered Tracks'))]
    ).transform_filter(brush)

    # Final
    final_elevation = alt.layer(elevation_back, elevation).add_params(brush
                ).properties(width=300, height=300, title='Elevation Gain Distribution of Registered Tracks')

    # Final chart
    final_chart = alt.vconcat(alt.hconcat(final_distance, final_time), alt.hconcat(final_pace, final_elevation))
    return final_chart