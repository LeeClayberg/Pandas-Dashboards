import pandas

# Link: https://www.kaggle.com/gregorut/videogamesales

df = pandas.read_csv("08-VideoGames/vgsales.csv", index_col=0)

# The total worldwide sales in millions by each genre
genre_sales = df.groupby('Genre').sum().sort_values('Global_Sales', ascending=False)['Global_Sales']

# The top five companies who have the highest total sales (in millions fo dollars)
company_sales = df.groupby('Publisher').sum().sort_values('Global_Sales', ascending=False)['Global_Sales'].head(5)

# The total sales by year in millions of dollars
year_sales = df.groupby('Year').sum()['Global_Sales']

# Most popular platform by year
platform_sales_with_year = df.groupby(['Year', 'Platform']).sum()['Global_Sales'].reset_index().groupby('Year').max()['Platform']

# Games per genre
games_per_genre = df.groupby('Genre').count().sort_values('Global_Sales', ascending=False)['Global_Sales']

# Company with the most sales for each platform
platform_company = df.groupby(['Platform', 'Publisher']).sum()['Global_Sales'].reset_index().groupby('Platform').max()['Publisher']

# Total sales for game regardless of platform
total_sales = df.groupby('Name').sum().sort_values('Global_Sales', ascending=False)['Global_Sales'].head(5)

# All pokemon games
pokemon_games = df.loc[df['Name'].str.contains('Pokemon')]

# First Nintendo game
first_nintendo = df.loc[df['Publisher'] == 'Nintendo'].sort_values(by='Year', ascending=True)[['Name', 'Year']].head(1)

# North America top 10 sellers
na_top_seller = df.sort_values(by='NA_Sales', ascending=False)[['Name', 'Publisher', 'NA_Sales']].head(10)

# What genre sells the best (ie highest avg sales)
genre_avg_sales = df.groupby('Genre').mean().sort_values('Global_Sales', ascending=False)['Global_Sales']

# Number of entries where the platform name is in the name of the game
platform_not_in_name = len(df.loc[df.apply(lambda x: x.Platform in x.Name, axis=1)])

# All super mario bros games
mario_games = df.loc[df['Name'].str.contains('Super Mario Bros')].sort_values(by='Year').reset_index()[['Year', 'Name', 'Global_Sales']]

print(mario_games)
