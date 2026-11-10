# Disaster Management Analytics

## Project Overview
Disaster Management Analytics is a data analytics project designed to analyze disaster-related incidents, emergency response operations, shelter availability, relief distribution, resources, weather conditions, and communication coverage.

The project uses Python, Streamlit, Pandas, Data Visualization, and Power BI to support disaster data analysis and decision-making.

## Key Features
- Interactive Streamlit frontend.
- Upload CSV datasets through the application.
- Analyze uploaded disaster management data.
- Incident and severity analysis.
- Emergency response time analysis.
- Shelter capacity and occupancy analysis.
- Relief distribution and resource analysis.
- Locality-based risk analysis.
- Power BI dashboard and visualizations.

## Technologies Used
- Python
- Streamlit
- Pandas
- Matplotlib
- Seaborn
- Power BI
- Git and GitHub

## Project Datasets
The project includes:
- incidents.csv
- shelters.csv
- responses.csv
- relief.csv
- population.csv
- resources.csv
- weather.csv
- communication.csv

## Project Structure
```text
Disaster-Management-Analytics/
│
├── app.py
├── generate_data.py
├── disaster_analysis.py
├── visualization.py
├── requirements.txt
├── Power_Bi_dashboard.pbix
│
├── data/
│   ├── incidents.csv
│   ├── shelters.csv
│   ├── responses.csv
│   ├── relief.csv
│   ├── population.csv
│   ├── resources.csv
│   ├── weather.csv
│   └── communication.csv
│
└── outputs/
    └── charts/
```

## Installation and Execution

1. Clone the repository:

```bash
git clone https://github.com/sayanbiswas425/Disaster-Management-Analytics.git
```

2. Open the project folder:

```bash
cd Disaster-Management-Analytics
```

3. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

4. Run the Streamlit application:

```bash
python -m streamlit run app.py
```

5. Open the local URL displayed in the terminal and upload the required CSV datasets through the application.

## Power BI Dashboard
The project also includes a Power BI dashboard file named `Power_Bi_dashboard.pbix`.

## Repository
https://github.com/sayanbiswas425/Disaster-Management-Analytics

## Project Purpose
To demonstrate how data analytics and visualization can help understand disaster situations, evaluate emergency response performance, and support better disaster management decisions.
