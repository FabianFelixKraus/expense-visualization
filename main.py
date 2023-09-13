import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def import_data(file_name="./input-data/example-input.csv"):
    """ 
    Imports csv file with this heading:
    Date (YYYY-MM-DD as UTC),Merchant,Txn Amount (Funding Card),Txn Currency (Funding Card),Txn Amount (Foreign Spend),Txn Currency (Foreign Spend),Card Name,Card Last 4 Digits,Type,Category,Notes
    into a pandas dataframe
    """

    return pd.read_csv(file_name)


def create_visualization(data):
    """
    Creates a bar graph using matplotlib where the x-axis is each month and the y-axis is the sum of the stacked transactions grouped by Category in this month 
    """

    def get_months(dates):
        """
        Gets a List of dates in the format of YYYY-MM-DD and returns every YYYY-MM that exists in the given array in ascending order
        """

        months = []
        for date in dates:
            part = date.split("-")[0]+"-"+date.split("-")[1]
            if not part in months:
                months.append(part)

        months.reverse()

        return months
        
    
    def get_categories(data):
        """
        Returns a list of all existing categories in the dataset
        """
        return list(set(data["Category"]))
    
    def get_transaction_volume_per_category_per_month(data,months,categories):
        """
        Returns a dictionary with categories as keys and a np.array of the transaction volume for each month corresponding to the category
        """

        def get_transactions_per_category_per_month(data, category, month):
            """ 
            Returns all transactions of data that have the given category and month with the format YYYY-MM
            """
            return data[(data["Date (YYYY-MM-DD as UTC)"].str.contains(month)) & (data["Category"] == category) & (data["Type"] != "Declined")]

        result = dict()

        for category in categories:
            transaction_volumes = []
            for month in months:
                transactions_per_category_per_month  = get_transactions_per_category_per_month(data, category, month)
                transaction_volumes.append(round(transactions_per_category_per_month["Txn Amount (Funding Card)"].sum(), 2))
            result[category] = transaction_volumes

        return result
    
    def adjust_transaction_volume_per_category_per_month(transaction_volume_per_category,months):
        """
        Adjust the dictionary with your own will
        """

        # Example: rename "Service" to "Washing" in the dictionary
        # if "Service" in transaction_volume_per_category:
        #     transaction_volume_per_category["Washing"] = transaction_volume_per_category.pop("Service")
        return transaction_volume_per_category, months

    def analyze_transaction_volume_per_category_per_month(transaction_volume_per_category, months):
        """
        Analyse the transactions and categories and return a dictionary with the analysis
        """
        def calc_median_expense(transaction_volume_per_category):
            # Calculates the median expense of all categories
            expenses = [sum(transaction_volume_per_category[category]) for category in transaction_volume_per_category]
            return round(np.median(expenses), 2)  

        def calc_avg_expense(transaction_volume_per_category):
            # Calculates the average expense of all categories
            expenses = [sum(transaction_volume_per_category[category]) for category in transaction_volume_per_category]
            return round(np.mean(expenses), 2)

        def calc_median_expense_per_category(transaction_volume_per_category):
            # Calculates the median expense of each category
            return {category: round(np.median(transaction_volume_per_category[category]), 2) for category in transaction_volume_per_category}

        def calc_avg_expense_per_category(transaction_volume_per_category):
            # Calculates the average expense of each category
            return {category: round(np.mean(transaction_volume_per_category[category]), 2) for category in transaction_volume_per_category}

        return { 
            "median_expense": calc_median_expense(transaction_volume_per_category),
            "avg_expense": calc_avg_expense(transaction_volume_per_category),
            "median_expense_per_category": calc_median_expense_per_category(transaction_volume_per_category),
            "avg_expense_per_category": calc_avg_expense_per_category(transaction_volume_per_category),
        }


    def create_bar_graph(transaction_volume_per_category, months):
        """
        Creates a bar graph using matplotlib where the x-axis is each month and the y-axis shows the spend amount in this month grouped by Category
        """
        def add_analysis_bar(analysis_type):
            """
            Modifies transaction_volume_per_category and months to include the analysis_type-bar
            """
            #Extend months
            months.extend([analysis_type])

            #Extend transaction_volume_per_category
            for category in transaction_volume_per_category:
                transaction_volume_per_category[category].extend([analysis_results[analysis_type][category]])
            

        fig, ax = plt.subplots()
        bottom = np.zeros(len(months)+2)

        width = 0.4

        # Calculate analysis results after extending the months list
        analysis_results = analyze_transaction_volume_per_category_per_month(transaction_volume_per_category, months)

        # Display analysis results
        print(f"Die durchschnittlichen Ausgaben betragen {analysis_results['avg_expense']}€")
        print(f"Die medianen Ausgaben betragen {analysis_results['median_expense']}€")

        add_analysis_bar("avg_expense_per_category")
        add_analysis_bar("median_expense_per_category")

        for category, transaction_volume_per_category_per_month in transaction_volume_per_category.items():
            p = ax.bar(months, transaction_volume_per_category_per_month, width, label=category, bottom=bottom)
            bottom = transaction_volume_per_category_per_month
            # Display labels for values not equal to 0 and make them smaller
            ax.bar_label(p, label_type='center')

        display_months = [month[1] + "." + month[0] for month in [month[2:].split("-") for month in months[:-2]]] + ["Durchschnitt", "Median"]
        ax.set_title(f'Kategorisierte monatliche Ausgaben von {display_months[0]} bis {display_months[-3]} \n')
        ax.set_ylabel('Ausgaben in €')
        ax.set_xlabel('Monat')
        ax.set_xticklabels(display_months, rotation=45)
        ax.legend()

        # Save the plot as an SVG & PNG file
        plt.savefig('./output/example-bar-chart.svg', format='svg', bbox_inches='tight')
        plt.savefig('./output/example-bar-chart.png', format='png', bbox_inches='tight')

        plt.show()


    months = get_months(data["Date (YYYY-MM-DD as UTC)"])
    categories = get_categories(data)
    transactions_per_month = get_transaction_volume_per_category_per_month(data,months,categories)
    create_bar_graph(*adjust_transaction_volume_per_category_per_month(transactions_per_month,months))


print(create_visualization(import_data()))

