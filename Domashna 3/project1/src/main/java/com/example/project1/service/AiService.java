package com.example.project1.service;

import com.example.project1.model.PriceLogEntity;
import com.example.project1.repository.PriceLogRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.cglib.core.Local;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class AiService {

    private final RestTemplate restTemplate = new RestTemplate();
    private final PriceLogRepository priceLogRepository;

    private final String predictionApiUrl = "http://127.0.0.1:8000/predict-next-month-price/";
    private final String pythonServerUrl = "http://127.0.0.1:8000";

    public Double predictNextMonth(Long companyId) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        List<PriceLogEntity> data = priceLogRepository.findByCompanyIdAndDateBetween(companyId, LocalDate.now().minusMonths(1), LocalDate.now());
        ;

        Map<String, Object> requestBody = Map.of("data", mapToRequestData(data));

        HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestBody, headers);

        Map<String, Double> response = restTemplate.postForObject(predictionApiUrl, requestEntity, Map.class);

        return response != null ? response.get("predicted_next_month_price") : null;


    }

    public static List<Map<String, Object>> mapToRequestData(List<PriceLogEntity> historicalDataEntities) {
        return historicalDataEntities.stream().map(entity -> {
            Map<String, Object> dataMap = new HashMap<>();
            dataMap.put("date", entity.getDate().toString());
            dataMap.put("average_price", entity.getAveragePrice());
            return dataMap;
        }).collect(Collectors.toList());
    }


    //=======================================================================================================
    public Map<String, Map<String, String>> generateSignalsByTimeframe(Long companyId) {
        Map<String, Map<String, String>> signalsByTimeframe = new HashMap<>();

        //last month logs for company
        var priceLogs = priceLogRepository.findByCompanyIdAndDateBetween(companyId, LocalDate.now(), LocalDate.now().minusDays(30));

        // Generate signals for 1 day timeframe
//        List<PriceLogEntity> dayLogs = filterByTimeframe(priceLogs, 1);
//        Map<String, List<Double>> dayOscillators = calculateOscillators(dayLogs);
//        Map<String, String> daySignals = generateSignal(dayOscillators);
//        signalsByTimeframe.put("day", daySignals);
//
//        // Generate signals for 1 week timeframe
//        List<PriceLogEntity> weekLogs = filterByTimeframe(priceLogs, 7);
//        Map<String, List<Double>> weekOscillators = calculateOscillators(weekLogs);
//        Map<String, String> weekSignals = generateSignal(weekOscillators);
//        signalsByTimeframe.put("week", weekSignals);

        // Generate signals for 1 month timeframe
        List<PriceLogEntity> monthLogs = filterByTimeframe(priceLogs, 30);
        monthLogs = priceLogs;
        Map<String, List<Double>> monthOscillators = calculateOscillators(monthLogs);
        Map<String, String> monthSignals = generateSignal(monthOscillators);
        signalsByTimeframe.put("month", monthSignals);

        return signalsByTimeframe;
    }

    // Helper method to filter the data for a specific timeframe, redundant can use priceLogRepository.findByCompanyIdAndDateBetween() TODO
    private List<PriceLogEntity> filterByTimeframe(List<PriceLogEntity> priceLogs, int daysBack) {
        LocalDate now = LocalDate.now();
        LocalDate cutoffDate = now.minusDays(daysBack);
        return priceLogs.stream()
                .filter(log -> log.getDate().isAfter(cutoffDate))
                .collect(Collectors.toList());
    }

    public Map<String, String> calculateOscillatorSignals(List<PriceLogEntity> priceLogs) {
        List<Double> prices = extractPrices(priceLogs);

        // Constants for calculation (periods)
        int RSI_PERIOD = 14;
        int STOCH_PERIOD = 14;
        int WILLIAMS_R_PERIOD = 14;
        int CCI_PERIOD = 14;

        // Calculate individual oscillators
        List<Double> rsiValues = calculateRSI(prices, RSI_PERIOD);
        List<Double> stochRSIValues = calculateStochasticOscillator(prices, STOCH_PERIOD);
        List<Double> williamsRValues = calculateWilliamsR(prices, WILLIAMS_R_PERIOD);
        List<Double> cciValues = calculateCCI(prices, CCI_PERIOD);

        // Generate signals based on the calculated values
        Map<String, String> signals = new HashMap<>();
        signals.put("RSI", generateRSISignal(rsiValues));
        signals.put("Stochastic RSI", generateStochRSISignal(stochRSIValues));
        signals.put("Williams %R", generateWilliamsRSignal(williamsRValues));
        signals.put("CCI", generateCCISignal(cciValues));

        return signals;
    }

    private String generateRSISignal(List<Double> rsiValues) {
        if (rsiValues.isEmpty()) {
            return "Hold"; // Default if no values are present
        }
        double latestRsi = rsiValues.get(rsiValues.size() - 1);
        if (latestRsi < 30) {
            return "Buy";
        } else if (latestRsi > 70) {
            return "Sell";
        } else {
            return "Hold";
        }
    }

    private String generateStochRSISignal(List<Double> stochRSIValues) {
        if (stochRSIValues.isEmpty()) {
            return "Hold"; // Default if no values are present
        }
        double latestStochRsi = stochRSIValues.get(stochRSIValues.size() - 1);
        if (latestStochRsi < 0.2) {
            return "Buy";
        } else if (latestStochRsi > 0.8) {
            return "Sell";
        } else {
            return "Hold";
        }
    }

    private String generateWilliamsRSignal(List<Double> williamsRValues) {
        if (williamsRValues.isEmpty()) {
            return "Hold"; // Default if no values are present
        }
        double latestWilliamsR = williamsRValues.get(williamsRValues.size() - 1);
        if (latestWilliamsR < -80) {
            return "Buy";
        } else if (latestWilliamsR > -20) {
            return "Sell";
        } else {
            return "Hold";
        }
    }

    private String generateCCISignal(List<Double> cciValues) {
        if (cciValues.isEmpty()) {
            return "Hold"; // Default if no values are present
        }
        double latestCci = cciValues.get(cciValues.size() - 1);
        if (latestCci > 100) {
            return "Buy";
        } else if (latestCci < -100) {
            return "Sell";
        } else {
            return "Hold";
        }
    }

    public Map<String, List<Double>> calculateOscillators(List<PriceLogEntity> priceLogs) {
        List<Double> prices = extractPrices(priceLogs);

        // Constants for calculation (periods)
        int RSI_PERIOD = 14;
        int STOCH_PERIOD = 14;
        int WILLIAMS_R_PERIOD = 14;
        int CCI_PERIOD = 14;

        // Initialize a map to store oscillator results
        Map<String, List<Double>> oscillatorResults = new HashMap<>();

        // Calculate RSI
        List<Double> rsiValues = calculateRSI(prices, RSI_PERIOD);
        oscillatorResults.put("RSI", rsiValues);

        // Calculate Stochastic Oscillator (StochRSI)
        List<Double> stochRSIValues = calculateStochasticOscillator(prices, STOCH_PERIOD);
        oscillatorResults.put("Stochastic RSI", stochRSIValues);

        // Calculate Williams %R
        List<Double> williamsRValues = calculateWilliamsR(prices, WILLIAMS_R_PERIOD);
        oscillatorResults.put("Williams %R", williamsRValues);

        // Calculate CCI
        List<Double> cciValues = calculateCCI(prices, CCI_PERIOD);
        oscillatorResults.put("CCI", cciValues);

        // Return the map with all the calculated oscillator values
        return oscillatorResults;
    }

    // Define thresholds for signals
    private static final double RSI_OVERBOUGHT = 70.0;
    private static final double RSI_OVERSOLD = 30.0;
    private static final double STOCH_RSI_OVERBOUGHT = 0.8;
    private static final double STOCH_RSI_OVERSOLD = 0.2;
    private static final double WILLIAMS_R_OVERBOUGHT = -20.0;
    private static final double WILLIAMS_R_OVERSOLD = -80.0;
    private static final double CCI_OVERBOUGHT = 100.0;
    private static final double CCI_OVERSOLD = -100.0;

    public Map<String, String> generateSignal(Map<String, List<Double>> oscillatorResults) {

        // Create a map to store the signals for each oscillator
        Map<String, String> signals = new HashMap<>();

        // Get the last value for each oscillator
        double rsi = oscillatorResults.get("RSI").get(oscillatorResults.get("RSI").size() - 1);
        double stochRSI = oscillatorResults.get("Stochastic RSI").get(oscillatorResults.get("Stochastic RSI").size() - 1);
        double williamsR = oscillatorResults.get("Williams %R").get(oscillatorResults.get("Williams %R").size() - 1);
        double cci = oscillatorResults.get("CCI").get(oscillatorResults.get("CCI").size() - 1);

        // Generate RSI Signal
        if (rsi > RSI_OVERBOUGHT) {
            signals.put("RSI", "Sell (RSI Overbought)");
        } else if (rsi < RSI_OVERSOLD) {
            signals.put("RSI", "Buy (RSI Oversold)");
        } else {
            signals.put("RSI", "Hold (RSI Neutral)");
        }

        // Generate Stochastic RSI Signal
        if (stochRSI > STOCH_RSI_OVERBOUGHT) {
            signals.put("Stochastic RSI", "Sell (Stochastic RSI Overbought)");
        } else if (stochRSI < STOCH_RSI_OVERSOLD) {
            signals.put("Stochastic RSI", "Buy (Stochastic RSI Oversold)");
        } else {
            signals.put("Stochastic RSI", "Hold (Stochastic RSI Neutral)");
        }

        // Generate Williams %R Signal
        if (williamsR > WILLIAMS_R_OVERBOUGHT) {
            signals.put("Williams %R", "Sell (Williams %R Overbought)");
        } else if (williamsR < WILLIAMS_R_OVERSOLD) {
            signals.put("Williams %R", "Buy (Williams %R Oversold)");
        } else {
            signals.put("Williams %R", "Hold (Williams %R Neutral)");
        }

        // Generate CCI Signal
        if (cci > CCI_OVERBOUGHT) {
            signals.put("CCI", "Sell (CCI Overbought)");
        } else if (cci < CCI_OVERSOLD) {
            signals.put("CCI", "Buy (CCI Oversold)");
        } else {
            signals.put("CCI", "Hold (CCI Neutral)");
        }

        // If all signals are "Hold", return a general hold signal
        if (!signals.containsValue("Buy") && !signals.containsValue("Sell")) {
            signals.put("Overall", "Hold");
        }

        return signals;
    }


    // Helper method to extract prices from PriceLogEntity
    private List<Double> extractPrices(List<PriceLogEntity> priceLogs) {
        List<Double> prices = new ArrayList<>();
        for (PriceLogEntity log : priceLogs) {
            prices.add(log.getAveragePrice());
        }
        return prices;
    }

    // Method to calculate RSI (Relative Strength Index)
    private List<Double> calculateRSI(List<Double> prices, int period) {
        List<Double> rsiValues = new ArrayList<>();
        for (int i = period; i < prices.size(); i++) {
            double avgGain = 0.0, avgLoss = 0.0;
            for (int j = i - period + 1; j <= i; j++) {
                double change = prices.get(j) - prices.get(j - 1);
                if (change > 0) {
                    avgGain += change;
                } else {
                    avgLoss -= change;
                }
            }
            avgGain /= period;
            avgLoss /= period;

            if (avgLoss == 0) {
                rsiValues.add(100.0);
            } else {
                double rs = avgGain / avgLoss;
                double rsi = 100 - (100 / (1 + rs));
                rsiValues.add(rsi);
            }
        }
        return rsiValues;
    }

    // Method to calculate Stochastic Oscillator (Stochastic RSI)
    private List<Double> calculateStochasticOscillator(List<Double> prices, int period) {
        List<Double> stochRSIValues = new ArrayList<>();
        for (int i = period; i < prices.size(); i++) {
            double minPrice = Double.MAX_VALUE;
            double maxPrice = -Double.MAX_VALUE;
            for (int j = i - period + 1; j <= i; j++) {
                minPrice = Math.min(minPrice, prices.get(j));
                maxPrice = Math.max(maxPrice, prices.get(j));
            }
            double stochRSI = (prices.get(i) - minPrice) / (maxPrice - minPrice);
            stochRSIValues.add(stochRSI);
        }
        return stochRSIValues;
    }

    // Method to calculate Williams %R
    private List<Double> calculateWilliamsR(List<Double> prices, int period) {
        List<Double> williamsRValues = new ArrayList<>();
        for (int i = period; i < prices.size(); i++) {
            double highestHigh = -Double.MAX_VALUE;
            double lowestLow = Double.MAX_VALUE;
            for (int j = i - period + 1; j <= i; j++) {
                highestHigh = Math.max(highestHigh, prices.get(j));
                lowestLow = Math.min(lowestLow, prices.get(j));
            }
            double williamsR = ((highestHigh - prices.get(i)) / (highestHigh - lowestLow)) * -100;
            williamsRValues.add(williamsR);
        }
        return williamsRValues;
    }

    // Method to calculate CCI (Commodity Channel Index)
    private List<Double> calculateCCI(List<Double> prices, int period) {
        List<Double> cciValues = new ArrayList<>();
        for (int i = period; i < prices.size(); i++) {
            double sum = 0.0;
            for (int j = i - period + 1; j <= i; j++) {
                sum += prices.get(j);
            }
            double mean = sum / period;
            double meanDeviation = 0.0;
            for (int j = i - period + 1; j <= i; j++) {
                meanDeviation += Math.abs(prices.get(j) - mean);
            }
            meanDeviation /= period;
            double cci = (prices.get(i) - mean) / (0.015 * meanDeviation);
            cciValues.add(cci);
        }
        return cciValues;
    }


}
