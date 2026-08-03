from datetime import datetime
from collections import defaultdict

class HistoricalEngine:
    """
    Engine to process raw historical AGMARKNET records into structured payload
    for the Historical Market Explorer frontend.
    """
    
    @staticmethod
    def process_historical_data(records):
        if not records:
            return {
                "summary": {},
                "insights": {},
                "monthly_summary": [],
                "market_performance": [],
                "ai_observations": "Insufficient data available to generate observations.",
                "raw_records": []
            }
            
        prices = [r['modal_price'] for r in records if r['modal_price'] > 0]
        arrivals = [r.get('arrival_quantity', 0) for r in records]
        
        avg_price = sum(prices) / len(prices) if prices else 0
        highest_price = max(prices) if prices else 0
        lowest_price = min(prices) if prices else 0
        avg_arrival = sum(arrivals) / len(arrivals) if arrivals else 0
        total_arrival = sum(arrivals)
        
        # Section 2: Summary
        summary = {
            "records_found": len(records),
            "average_price": round(avg_price, 2),
            "highest_price": highest_price,
            "lowest_price": lowest_price,
            "average_arrival": round(avg_arrival, 2),
            "latest_update": records[-1]['date'] if records else None
        }
        
        # Section 5: Insights
        insights = {
            "highest_recorded": highest_price,
            "lowest_recorded": lowest_price,
            "total_arrivals": round(total_arrival, 2),
            "average_movement": "N/A" # Complex to calculate in pure py, leaving simple
        }
        
        # Calculate daily price changes for largest increase/decrease
        daily_prices = {}
        for r in records:
            if r['date'] not in daily_prices:
                daily_prices[r['date']] = []
            if r['modal_price'] > 0:
                daily_prices[r['date']].append(r['modal_price'])
                
        sorted_dates = sorted(daily_prices.keys())
        largest_increase = 0
        largest_decrease = 0
        
        for i in range(1, len(sorted_dates)):
            prev_avg = sum(daily_prices[sorted_dates[i-1]]) / len(daily_prices[sorted_dates[i-1]])
            curr_avg = sum(daily_prices[sorted_dates[i]]) / len(daily_prices[sorted_dates[i]])
            diff = curr_avg - prev_avg
            if diff > largest_increase:
                largest_increase = diff
            if diff < largest_decrease:
                largest_decrease = diff
                
        insights["largest_increase"] = round(largest_increase, 2)
        insights["largest_decrease"] = round(abs(largest_decrease), 2)
        
        # Section 6: Monthly Summary
        monthly_data = defaultdict(lambda: {"prices": [], "arrivals": []})
        for r in records:
            month_key = r['date'][:7] # YYYY-MM
            if r['modal_price'] > 0:
                monthly_data[month_key]["prices"].append(r['modal_price'])
            monthly_data[month_key]["arrivals"].append(r.get('arrival_quantity', 0))
            
        monthly_summary = []
        for m, data in sorted(monthly_data.items()):
            m_prices = data["prices"]
            m_arrivals = data["arrivals"]
            monthly_summary.append({
                "month": m,
                "average_price": round(sum(m_prices) / len(m_prices), 2) if m_prices else 0,
                "highest_price": max(m_prices) if m_prices else 0,
                "lowest_price": min(m_prices) if m_prices else 0,
                "average_arrival": round(sum(m_arrivals) / len(m_arrivals), 2) if m_arrivals else 0,
            })
            
        # Section 7: Market Performance
        market_data = defaultdict(lambda: {"prices": [], "arrivals": []})
        for r in records:
            m_name = r['market']
            if r['modal_price'] > 0:
                market_data[m_name]["prices"].append(r['modal_price'])
            market_data[m_name]["arrivals"].append(r.get('arrival_quantity', 0))
            
        market_performance = []
        for m_name, data in market_data.items():
            m_prices = data["prices"]
            m_arrivals = data["arrivals"]
            avg = round(sum(m_prices) / len(m_prices), 2) if m_prices else 0
            market_performance.append({
                "market_name": m_name,
                "average_price": avg,
                "highest_price": max(m_prices) if m_prices else 0,
                "lowest_price": min(m_prices) if m_prices else 0,
                "average_arrival": round(sum(m_arrivals) / len(m_arrivals), 2) if m_arrivals else 0,
            })
            
        # Rank by average price
        market_performance.sort(key=lambda x: x['average_price'], reverse=True)
        for idx, perf in enumerate(market_performance):
            perf['rank'] = idx + 1
            
        # Section 8: AI Observations (Simple NLP generation based on stats)
        ai_obs = "During this period, prices remained relatively stable."
        if largest_increase > (avg_price * 0.1):
            ai_obs = f"We observed significant price volatility, with a major surge of ₹{round(largest_increase, 2)} in a single day."
        elif largest_decrease < -(avg_price * 0.1):
            ai_obs = f"Prices experienced downward pressure, including a sharp drop of ₹{round(abs(largest_decrease), 2)}."
            
        best_market = market_performance[0]['market_name'] if market_performance else "Unknown"
        ai_obs += f" {best_market} consistently offered the highest average modal price."
        
        return {
            "summary": summary,
            "insights": insights,
            "monthly_summary": monthly_summary,
            "market_performance": market_performance,
            "ai_observations": ai_obs,
            "raw_records": records
        }
