# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 18:07:33 2021

@author: John
"""
import numpy as np
import pandas as pd
import datetime
import seaborn as sns
import matplotlib.pyplot as plt
path = r'C:\Users\John\Documents\habit_tracker'

MAX_VALUE=2.5
MIN_VALUE=.25
MEAN_VALUE=.5
STD_VALUE=.5
ADDITIONAL_REWARDS=[]

class HabitTracker():
    '''
    habit_complete: marks down the habit and gives a random reward
    bad_habit: marks down habit and deducts a penalty
    use_reward: removes the reward that is used
    reset: deletes the excel sheet and creates a new blank one 
    set_reward: allows the user to set the current reward
    rename_habit: allows the user to rename a habit
    drop_habit: allows the user to drop a habit
    graph_streak: graphs the habit information
    math: provides averages and summations of habits
    get_data: returns the excel sheet as a dataframe and prints the current reward
    '''
    def __init__(self):
        try: 
            self.data = pd.read_excel(path+'\habit_tracker.xlsx').rename(
                columns={'Unnamed: 0': 'date'}).set_index('date')
        except FileNotFoundError:
            self.data = pd.DataFrame()
        except KeyError:
            self.data = pd.read_excel(path+'\habit_tracker.xlsx')
            print("If the excel sheet isn't empty check the data, "
                  'something went wrong')
        try:
            with open(f'{path}/reward.txt', 'r', encoding="utf-8") as file:
                self.reward_amount = float(file.read())
        except:
            self.reward_amount=0
            
    def reward(mean=MEAN_VALUE, std=STD_VALUE, 
               maximum=MAX_VALUE, minimum=MIN_VALUE):
        '''
        Parameters
        ----------
        mean : NUMERIC, optional
            DESCRIPTION. The default is MEAN_VALUE.
        std : NUMERIC, optional
            DESCRIPTION. The default is STD_VALUE.
        maximum : NUMERIC, optional
            DESCRIPTION. The default is MAX_VALUE.
        minimum : NUMERIC, optional
            DESCRIPTION. The default is MIN_VALUE.

        Returns
        -------
        reward : NUMERIC
            DESCRIPTION. A random number between maximum and minimum with a 
            mean of mean and a standard deviation of std
        '''
        reward = round(np.random.normal(loc=mean, scale=std), 2)
        reward = min(reward, maximum)
        reward = max(reward, minimum)
        return reward
    
    def test_nan(value):
        '''
        Tests if a value is missing (np.nan). True if missing
        '''
        try:
            np.testing.assert_equal(value,np.nan)
            return True
        except AssertionError:
            return False
    
    def habit_complete(self, habit, value=1, 
                       earn_reward=True, penalty=False, 
                       add=False, reward_num=1, date=False):
        '''
        Takes the habit's name and inputs the value in the habit's column.
        If earn_reward=True a random reward will be added to the reward and there
        is a 1% chance that an additional reward will be rewarded. If 
        penalty=True, the minimum reward will be deducted for every day the 
        habit was not done. If add=True, then the value will be added to the value
        that is already in the cell for habit today. reward_num is the number
        of rewards that will be applied, you also have that many chances to get
        an additional award if applicable, a max of 1 reward will be awarded.
        '''
        if date:
            try:
                datetime.datetime.strptime(date, '%m/%d/%Y')
                if len(date) != 10:
                    return print('The date should be in MM/DD/YYYY format')
                else:
                    try:
                        self.data.loc[date]
                    except:
                        return print('The date listed is not in the sheet, '
                                     'so no habit added. If you are backfilling'
                                     ' habits, first add a habit for today.')
            except:
                return print('The date should be in MM/DD/YYY format')
        else:
            day = str(datetime.datetime.today().day)
            if len(day)==1:
                day = '0'+day
            month = str(datetime.datetime.today().month)
            if len(month)==1:
                month = '0'+month
            year = datetime.datetime.today().year
            date = str(month)+'/'+str(day)+'/'+str(year)
        current = datetime.datetime.strptime(date, '%m/%d/%Y')
        if add:
            try:
                val = value + self.data[habit][date]
                if HabitTracker.test_nan(val):
                    print(f'No value for {habit} on {date}, so {value} was added')
                else:
                    value = val
                    print(f'The new value for {habit} is {value}')
            except:
                print(f'No value for {habit} on {date}, so {value} was added')
        try:
            recent_date = self.data.iloc[len(self.data)-1].name
            previous = datetime.datetime.strptime(recent_date, '%m/%d/%Y')
            date_lst=pd.date_range(previous, current, freq='d')
            date_lst = [x.strftime('%m/%d/%Y') for x in date_lst if x not in [current, previous]]
            if date_lst:
                for i in date_lst:
                    try:
                        self.data.at[i,habit]=np.nan
                    except KeyError:
                        addition = pd.DataFrame(index=[i], columns=[habit])
                        pd.concat(self.data,addition)   
        except:
            print("If the excel sheet isn't empty, something went wrong.")
        try:
            self.data.at[date,habit]=value
        except KeyError:
            addition = pd.DataFrame(index=[date], columns=[habit])
            pd.concat(self.data,addition)
        self.data.to_excel(rf'{path}/habit_tracker.xlsx') 
        if earn_reward:
            total_reward=0
            for num in range(reward_num):
                new_reward = HabitTracker.reward()
                self.reward_amount += new_reward
                total_reward += new_reward
            print(f'Your reward is {round(total_reward,2)}')
            if ADDITIONAL_REWARDS:
                extra=False
                count=1
                while not extra and count <= reward_num:
                    count+=1
                    extra = np.random.choice([True, False], p=[0.01, 0.99])
                if extra:
                    prize = np.random.choice(ADDITIONAL_REWARDS)
                    print(f'CONGRATULATIONS! You have won the bonus prize: {prize}')        
        if penalty: 
            day = np.nan
            count = 0
            for i in range(len(self.data[habit])):
                day = self.data.iloc[len(self.data[habit])\
                         -(i+2)][list(self.data.columns).index(habit)]
                if HabitTracker.test_nan(day):
                    count+=1
                if not HabitTracker.test_nan(day):
                    break
            reward_penalty = MIN_VALUE*count
            self.reward_amount -= reward_penalty
            if count > 0:
                print(f'You skipped {count} day(s)... You shall be '
                      f"penalized {reward_penalty}")
        with open(f'{path}/reward.txt', 'w') as f:
            f.write(str(self.reward_amount))        
        print(f'Your total reward is {round(self.reward_amount,2)}')
        
    def bad_habit(self, habit, value=1, penalize=True, 
                  penalty=1, add=False, date=False):
        '''
        Takes the habit's name and inputs the value in the habit's column.
        If penalize=True penalty will be deducted from the reward equal to the
        minumum reward multiplied by penalty. If penalize=False, then no penalty
        is deducted, but the bad habit is recorded. If add=True, then the value 
        will be added to the value that is already in the cell for habit today.
        '''
        if date:
            try:
                datetime.datetime.strptime(date, '%m/%d/%Y')
                if len(date) != 10:
                    return print('The date should be in MM/DD/YYYY format')
                else:
                    try:
                        self.data.loc[date]
                    except:
                        return print('The date listed is not in the sheet, '
                                     'so no habit added. If you are backfilling'
                                     ' habits, first add a habit for today.')
            except:
                return print('The date should be in MM/DD/YYY format')
        else:
            day = str(datetime.datetime.today().day)
            if len(day)==1:
                day = '0'+day
            month = str(datetime.datetime.today().month)
            if len(month)==1:
                month = '0'+month
            year = datetime.datetime.today().year
            date = str(month)+'/'+str(day)+'/'+str(year)
        if add:
            try:
                value = value + self.data[habit][date]
            except:
                print(f'No value for {habit} on {date}, so {value} was added')
        try:
            self.data.at[date,habit]=value
        except KeyError:
            addition = pd.DataFrame(index=[date], columns=[habit])
            pd.concat(self.data,addition)
        self.data.to_excel(rf'{path}/habit_tracker.xlsx') 
        if penalize:
            new_penalty = MIN_VALUE*penalty
            self.reward_amount -= new_penalty
            with open(f'{path}/reward.txt', 'w') as f:
                f.write(str(self.reward_amount))        
            print(f'For shame... Your penalty is {round(new_penalty,2)}, '
                  'and your action has been cataloged')
            print(f'Your total reward is now {round(self.reward_amount,2)}')
        else:
            print('You escape penalty, but your shame has been recorded.')

    def use_reward(self, value, do_it_anyway=False):
        '''
        Deducts value from the reward. If the value is larger than the reward,
        an error will occur. If value>reward and do_it_anyway=True, then the
        reward will be set to 0.
        '''
        if self.reward_amount >= value:
            self.reward_amount -= value
            print(f'your current balance is {round(self.reward_amount,2)}')
            with open(f'{path}/reward.txt', 'w') as f:
                f.write(str(self.reward_amount))
        elif do_it_anyway:
            new_value = self.reward_amount - value
            self.reward_amount = 0
            with open(f'{path}/reward.txt', 'w') as f:
                f.write(str(self.reward_amount))
            print(f'You have used too much money, shame. You went '
                  f"{round(abs(new_value),2)} over. You're amount is now 0")
        else:
            new_value = self.reward_amount - value
            print('You do not have the funds to pay for this. You need '
                  f'{round(abs(new_value),2)} more. If you want to '
                  'take out this amount anyway specify do_it_anyway=True')
    
    def reset(self):
        '''
        The excel sheet where all of the data is stored will be deleted and 
        a blank excel sheet will be saved in its place. The method will ask
        you twice if you are sure you want to go through with this. You must 
        answer 'yes' both times for the excel sheet to be deleted.
        '''
        answer = str(input('Are you sure? There is no going back: ')).strip()
        if answer.lower() == 'yes':
            answer = str(input('Are you really sure?: ')).strip()
            if answer.lower() == 'yes':
                reset_df = pd.DataFrame()
                reset_df.to_excel(rf'{path}/habit_tracker.xlsx') 
                self.data = reset_df
                print('It shall be done')  
            else:
               print("Okay, you're excel sheet won't be reset") 
        else:
            print("Okay, you're excel sheet won't be reset")
            
    def set_reward(self, value):
        '''
        The current reward (self.reward_amount) will be replaced with value.
        You will be asked if you are sure you want to do this, to proceed, 
        you must answer 'yes'.

        '''
        answer = str(input('Are you sure you want to change the reward?: ')).strip()
        if answer.lower() == 'yes':
            self.reward_amount = value
            with open(f'{path}/reward.txt', 'w') as f:
                f.write(str(self.reward_amount))
            print(f"You're new reward is {self.reward_amount}")
        else:
            print(f"You're reward is still {round(self.reward_amount,2)}")
            
    def rename_habit(self, current_name, new_name):
        '''
        The habit specified will be renamed to new_name. This change will be saved to
        the excel sheet as well.
        '''
        self.data = self.data.rename(columns={current_name:new_name})
        self.data.to_excel(rf'{path}/habit_tracker.xlsx') 
        print(f'{current_name} has been renamed to {new_name}')

    def drop_habit(self, habit):
        '''
        The habit specified will be droped from the data and the excel sheet.

        '''
        answer = str(input(f'Are you sure you want to drop {habit}? There is no going back: ')).strip()
        if answer.lower() == 'yes':
            self.data = self.data.drop(habit, axis=1)
            self.data.to_excel(rf'{path}/habit_tracker.xlsx') 
            print(f'{habit} has been removed from the data and the excel sheet.')
        else:
            print(f'{habit} was not dropped')
            
    def graph_streak(self, value, graph_type='line', 
                     value_name=False, range_dates=False):
        '''
        Produces a plot of value. The default graph_type is a 'line' which 
        produces a line graph of the values in the cells. value_name allows you 
        to label the y-axis on this line graph. graph_type can also be set to 
        'step' which will produce a step graph that displays what days the habit
        was completed and which days it wasn't. graph_type can also be 'bar'
        which will result in a two bars, one indicating the number of days the
        habit was completed, and the other indicating the number of days it wasn't.
        range_dates allows you to set the date range the graph will be over.

        '''
        if not range_dates:
            range_dates = [self.data.index[0], self.data.index[-1]]
        date_range = self.data.loc[range_dates[0]:range_dates[1]]
        #Removes year from date and removes leading zeros from days and months
        date_lst = [x[:5].replace('0','') if x[0] == '0' and x[3] == '0' \
                    else x[:5].lstrip('0') if x[0] == '0' \
                    else x[:3]+x[4:5] if x[3] == '0' else x[:5] \
                    for x in date_range.index]
        binary_lst = [0 if HabitTracker.test_nan(x) == True else 1 for x in date_range[value]]
        cat_lst = ['Complete' if x == 1 else 'Missed' for x in binary_lst]
        if graph_type == 'line':
            fig, ax = plt.subplots()
            sns.lineplot(data=date_range, x=date_lst, y=value, 
                         sort=False, color='k')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.set_title(f'{value.capitalize()} Over Time')
            ax.set_xlabel('Date')
            if value_name:
                ax.set_ylabel(f'{value_name}')
            plt.xticks(rotation=45)
        elif graph_type == 'step':
            fig, ax = plt.subplots()
            sns.lineplot(x=date_lst, y=binary_lst, 
                         drawstyle='steps-mid', linewidth=15, 
                         color='k', sort=False)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.set_xlabel('Date')
            ax.set_title(f'{value.capitalize()} Streak')
            plt.yticks([0,1], ['Missed', 'Complete'])
            #Cite: https://stackoverflow.com/questions/12608788/changing-the-tick-frequency-on-x-or-y-axis-in-matplotlib
            start, end = ax.get_xlim()
            ax.xaxis.set_ticks(np.arange(start, end, 2))
            plt.xticks(rotation=45)
        elif graph_type == 'bar':
            fig, ax = plt.subplots()
            sns.countplot(cat_lst, palette=['g','r'], 
                          order=['Complete', 'Missed'])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.set_title(f'{value.capitalize()} Totals')
            ax.set_ylabel('')
            plt.yticks([cat_lst.count('Complete'),cat_lst.count('Missed')])
        else:
            print('The graph type options are line, step, and bar.')
        
    def math(self, habit, func, count_nan=True):
        '''
        Provides descriptive data about the habit. func can be 'summation' 
        (which will sum the column), 'average' (which will find the average),
        or range (which will find the minimum value, the maximum value, and 
        the range). If count_nan=True then missing values are included in the 
        caluclations of the average.
        '''
        addition = sum(x for x in self.data[habit] if not HabitTracker.test_nan(x))
        if func == 'average':
            if count_nan:
                result = addition/len(self.data[habit])
                print(f'The average value for {habit} is {round(result,2)}')
            else:
                result = addition/len([x for x in self.data[habit] if not HabitTracker.test_nan(x)])
                print(f'The average value for {habit} on days you completed it'
                      f' is {round(result,2)}')
        elif func == 'summation':
            print(f'The total value for {habit} is {addition}') 
        elif func == 'range':
            print(f'The maximum value for {habit} is {max(self.data[habit])}')
            print(f'The minimum value for {habit} is {min(self.data[habit])}')
            print(f'The range for {habit} is '
                  f'{max(self.data[habit])-min(self.data[habit])}')
        else:
            print('func should either be average or summation')

    def get_data(self):
        '''
        Prints the current reward and returns the excel sheet with all the data.
        '''
        print(f'Your current reward is {round(self.reward_amount,2)}')
        return self.data
