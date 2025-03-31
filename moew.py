import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from bs4 import BeautifulSoup
import time
import re
from tqdm import tqdm

# Function to get sales data from VGChartz (example using web scraping)
def get_sales_data(year, platform='All'):
    print("Scaping data for year", year)
    """
    Scrape top games sales data for a given year
    
    Parameters:
        year (int): Year to gather data for
        platform (str): Platform filter or 'All'
        
    Returns:
        pandas.DataFrame: DataFrame with game sales data
    """
    games_data = []
    
    # This would be your actual scraping code
    # Example structure (you'd need to adapt to the actual site HTML):
    base_url = f"https://www.vgchartz.com/yearly/games/{year}/Global/"
    
    # In real implementation, you might need to paginate through results
    # Below is a placeholder for scraping logic
    try:
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find game entries in the table
        game_rows = soup.find_all('tr', class_='chart-row')  # Adjust selector based on actual HTML
        
        for row in game_rows:
            try:
                title = row.find('td', class_='title').text.strip()
                genre = row.find('td', class_='genre').text.strip()
                sales = float(row.find('td', class_='sales').text.replace('m', ''))  # Convert "5.2m" to 5.2
                publisher = row.find('td', class_='publisher').text.strip()
                
                games_data.append({
                    'title': title,
                    'genre': genre,
                    'sales': sales,  # In millions of units
                    'publisher': publisher,
                    'year': year
                })
            except (AttributeError, ValueError) as e:
                print(f"Error parsing row: {e}")
                continue
                
    except Exception as e:
        print(f"Error fetching data for {year}: {e}")
    
    # If web scraping is challenging, you might want to use a fallback sample dataset
    # This is just for demonstration - in a real project you'd use actual data
    if not games_data:
        print(f"Using sample data for {year}")
        # Create synthetic data for demonstration
        genres = ['Action', 'Adventure', 'RPG', 'Sports', 'Strategy', 'Racing', 
                 'Simulation', 'Fighting', 'Platformer', 'Puzzle', 'Shooter']
        
        # Generate random data with realistic trends
        # Base popularity that changes over time
        genre_trend = {
            'Shooter': 20 + (year - 2000) * 0.5,  # Growing genre
            'RPG': 15 + (year - 2000) * 0.3,
            'Action': 25 - (year - 2000) * 0.1,  # Slightly declining
            'Adventure': 10 + (year - 2000) * 0.2,
            'Sports': 15 - (year - 2000) * 0.05,
            'Strategy': 8 - (year - 2000) * 0.1,
            'Racing': 7 - (year - 2000) * 0.1,
            'Simulation': 5 + (year - 2000) * 0.3,
            'Fighting': 6 - (year - 2000) * 0.05,
            'Platformer': 10 - (year - 2000) * 0.2,
            'Puzzle': 4 + (year - 2000) * 0.1
        }
        
        # Generate 100 top games with appropriate distribution
        np.random.seed(year)  # For reproducibility but different for each year
        
        for i in range(100):
            # Weight genre selection by their popularity trends
            weights = [max(1, genre_trend.get(g, 5)) for g in genres]
            genre = np.random.choice(genres, p=np.array(weights)/sum(weights))
            
            # Sales are higher for more popular games/genres
            rank_factor = (100 - i) / 100  # Higher ranked games sell more
            genre_factor = genre_trend.get(genre, 5) / 20  # Popular genres sell more
            base_sales = 15 * rank_factor * genre_factor  # Base sales in millions
            
            # Add randomness
            sales = base_sales * (0.7 + 0.6 * np.random.random())
            
            games_data.append({
                'title': f"Game {i+1} ({year})",
                'genre': genre,
                'sales': round(sales, 2),
                'publisher': f"Publisher {(i % 20) + 1}",
                'year': year
            })
    
    return pd.DataFrame(games_data)

# Function to calculate market share by genre
def calculate_genre_market_share(start_year, end_year):
    """
    Calculate market share for each genre across years
    
    Parameters:
        start_year (int): First year to analyze
        end_year (int): Last year to analyze
        
    Returns:
        pandas.DataFrame: DataFrame with market share percentages by genre and year
    """
    all_data = []
    
    # Collect data for each year
    for year in tqdm(range(start_year, end_year + 1), desc="Collecting sales data"):
        year_data = get_sales_data(year)
        all_data.append(year_data)
        time.sleep(1)  # Be nice to servers
    
    # Combine all years
    all_games_df = pd.concat(all_data, ignore_index=True)
    
    # Calculate market share by genre for each year
    market_share_df = pd.DataFrame()
    
    for year in range(start_year, end_year + 1):
        year_data = all_games_df[all_games_df['year'] == year]
        
        if len(year_data) == 0:
            continue
            
        # Calculate total sales for the year
        total_sales = year_data['sales'].sum()
        
        # Group by genre and calculate market share
        genre_sales = year_data.groupby('genre')['sales'].sum()
        genre_market_share = (genre_sales / total_sales * 100).reset_index()
        genre_market_share['year'] = year
        
        market_share_df = pd.concat([market_share_df, genre_market_share], ignore_index=True)
    
    # Pivot for easier plotting
    market_share_pivot = market_share_df.pivot(index='year', columns='genre', values='sales')
    
    return market_share_pivot

# Function to visualize market share
def visualize_market_share(market_share_data, top_n=5, output_file='genre_market_share.png'):
    """
    Create visualizations for genre market share
    
    Parameters:
        market_share_data (pandas.DataFrame): Pivoted market share data
        top_n (int): Number of top genres to highlight
        output_file (str): Filename for saving the visualization
    """
    # Select top genres by average market share
    top_genres = market_share_data.mean().nlargest(top_n).index.tolist()
    
    # Create 'Other' category for remaining genres
    plot_data = market_share_data.copy()
    
    if len(market_share_data.columns) > top_n:
        other_genres = [col for col in market_share_data.columns if col not in top_genres]
        plot_data['Other'] = plot_data[other_genres].sum(axis=1)
        plot_data = plot_data[top_genres + ['Other']]
    
    # Create stacked area chart
    plt.figure(figsize=(12, 8))
    
    # Get a good color palette
    colors = sns.color_palette("husl", len(plot_data.columns))
    
    # Plot stacked area
    plt.stackplot(plot_data.index, 
                 [plot_data[genre] for genre in plot_data.columns],
                 labels=plot_data.columns,
                 colors=colors,
                 alpha=0.8)
    
    plt.title('Video Game Genre Market Share Over Time', fontsize=16)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Market Share (%)', fontsize=14)
    plt.xlim(plot_data.index.min(), plot_data.index.max())
    plt.ylim(0, 100)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(loc='upper right', fontsize=12)
    
    # Add percentage labels for the most recent year
    last_year = plot_data.index.max()
    last_year_data = plot_data.loc[last_year]
    
    # Save and show
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.show()
    
    # Also create a pie chart for the most recent year
    plt.figure(figsize=(10, 10))
    plt.pie(last_year_data, 
            labels=last_year_data.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            explode=[0.05 if genre == top_genres[0] else 0 for genre in last_year_data.index])
    
    plt.title(f'Video Game Genre Market Share ({last_year})', fontsize=16)
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(f'genre_pie_chart_{last_year}.png', dpi=300)
    plt.show()
    
    # Create a line chart showing evolution of top genres
    plt.figure(figsize=(12, 8))
    
    for genre in top_genres:
        plt.plot(plot_data.index, plot_data[genre], marker='o', linewidth=2, label=genre)
    
    plt.title('Market Share Evolution of Top Video Game Genres', fontsize=16)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Market Share (%)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.savefig('top_genres_trend.png', dpi=300)
    plt.show()

# Additional analysis function
def analyze_market_trends(market_share_data):
    """
    Perform additional analysis on market share trends
    
    Parameters:
        market_share_data (pandas.DataFrame): Pivoted market share data
        
    Returns:
        dict: Dictionary with analysis results
    """
    # Calculate growth rate for each genre
    first_year = market_share_data.index.min()
    last_year = market_share_data.index.max()
    
    results = {
        'fastest_growing': [],
        'fastest_declining': [],
        'most_stable': [],
        'market_concentration': []
    }
    
    # Growth rates
    for genre in market_share_data.columns:
        if genre in market_share_data.loc[first_year] and genre in market_share_data.loc[last_year]:
            first_share = market_share_data.loc[first_year, genre]
            last_share = market_share_data.loc[last_year, genre]
            
            if first_share > 0:  # Avoid division by zero
                growth_rate = ((last_share - first_share) / first_share) * 100
                change = last_share - first_share
                
                item = {
                    'genre': genre,
                    'growth_rate': round(growth_rate, 2),
                    'absolute_change': round(change, 2),
                    'start_share': round(first_share, 2),
                    'end_share': round(last_share, 2)
                }
                
                if growth_rate > 0:
                    results['fastest_growing'].append(item)
                else:
                    results['fastest_declining'].append(item)
    
    # Sort by growth rate
    results['fastest_growing'] = sorted(results['fastest_growing'], 
                                        key=lambda x: x['growth_rate'], reverse=True)[:3]
    results['fastest_declining'] = sorted(results['fastest_declining'], 
                                         key=lambda x: x['growth_rate'])[:3]
    
    # Calculate stability (lowest standard deviation)
    for genre in market_share_data.columns:
        std_dev = market_share_data[genre].std()
        mean_share = market_share_data[genre].mean()
        
        if mean_share > 1:  # Only consider genres with meaningful market share
            results['most_stable'].append({
                'genre': genre,
                'std_dev': round(std_dev, 2),
                'coefficient_of_variation': round((std_dev / mean_share) * 100, 2),
                'mean_share': round(mean_share, 2)
            })
    
    # Sort by coefficient of variation (lower is more stable)
    results['most_stable'] = sorted(results['most_stable'], 
                                   key=lambda x: x['coefficient_of_variation'])[:3]
    
    # Calculate market concentration over time (HHI - Herfindahl-Hirschman Index)
    for year in market_share_data.index:
        year_data = market_share_data.loc[year]
        # HHI is sum of squared market shares
        hhi = (year_data / 100) ** 2
        hhi_score = hhi.sum() * 10000  # Conventional HHI scale
        
        results['market_concentration'].append({
            'year': year,
            'hhi': round(hhi_score, 2),
            'concentration': 'High' if hhi_score > 2500 else 'Moderate' if hhi_score > 1500 else 'Low'
        })
    
    return results

# Main execution
if __name__ == "__main__":
    # Define year range
    START_YEAR = 2000
    END_YEAR = 2023
    
    # Calculate market share
    print("Calculating genre market share...")
    market_share = calculate_genre_market_share(START_YEAR, END_YEAR)
    
    # Save raw data
    market_share.to_csv('genre_market_share_data.csv')
    
    # Visualize the data
    print("Creating visualizations...")
    visualize_market_share(market_share, top_n=6)
    
    # Perform additional analysis
    print("Analyzing market trends...")
    trends = analyze_market_trends(market_share)
    
    # Print insights
    print("\n=== KEY INSIGHTS ===")
    
    print("\nFastest Growing Genres:")
    for genre in trends['fastest_growing']:
        print(f"• {genre['genre']}: +{genre['growth_rate']}% growth rate " +
              f"({genre['start_share']}% → {genre['end_share']}%)")
    
    print("\nFastest Declining Genres:")
    for genre in trends['fastest_declining']:
        print(f"• {genre['genre']}: {genre['growth_rate']}% growth rate " +
              f"({genre['start_share']}% → {genre['end_share']}%)")
    
    print("\nMost Stable Genres:")
    for genre in trends['most_stable']:
        print(f"• {genre['genre']}: {genre['coefficient_of_variation']}% coefficient of variation " +
              f"(average market share: {genre['mean_share']}%)")
    
    print("\nMarket Concentration (HHI):")
    first = trends['market_concentration'][0]
    last = trends['market_concentration'][-1]
    print(f"• {first['year']}: {first['hhi']} ({first['concentration']} concentration)")
    print(f"• {last['year']}: {last['hhi']} ({last['concentration']} concentration)")
    
    if first['hhi'] < last['hhi']:
        print(f"• Market concentration has increased by {round(last['hhi'] - first['hhi'], 2)} points")
    else:
        print(f"• Market concentration has decreased by {round(first['hhi'] - last['hhi'], 2)} points")