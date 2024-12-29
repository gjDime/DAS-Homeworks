package com.example.project1.service;

import com.example.project1.model.BusinessEntity;
import com.example.project1.model.PriceLogEntity;
import com.example.project1.model.dto.Response;
import com.example.project1.repository.BusinessRepository;
import com.example.project1.repository.PriceLogRepository;
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
public class BusinessCalcService {

    private final RestTemplate restTemplate = new RestTemplate();
    private final PriceLogRepository priceLogRepository;
    private final BusinessRepository businessRepository;

    private final String predictionApiUrl = "http://127.0.0.1:8000/predict-next-month/";
    private final String tehnicalsUrl = "http://127.0.0.1:5000/generate_signal";

    public BusinessCalcService(PriceLogRepository priceLogRepository, BusinessRepository businessRepository) {
        this.priceLogRepository = priceLogRepository;
        this.businessRepository = businessRepository;
    }

    public Map<String, String> technicalAnalysis(Long companyId) {
        final String tehnicalsUrl = "http://127.0.0.1:5000/market_signal";

        // Retrieve historical data from the repository
        List<PriceLogEntity> data = priceLogRepository.findByCompanyId(companyId);

        // Prepare the data to send to the Python API
        List<Map<String, Object>> payload = new ArrayList<>();
        for (PriceLogEntity d : data) {
            Map<String, Object> record = new HashMap<>();
            record.put("date", d.getDate().toString());
            record.put("close", d.getLastTransactionPrice());
            record.put("open", (d.getMaxPrice() + d.getMinPrice()) / 2.0);
            record.put("high", d.getMaxPrice());
            record.put("low", d.getMinPrice());
            record.put("volume", d.getQuantity());
            payload.add(record);
        }

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<List<Map<String, Object>>> requestEntity = new HttpEntity<>(payload, headers);
        ResponseEntity<Map> responseEntity = restTemplate.exchange(
                tehnicalsUrl,
                HttpMethod.POST,
                requestEntity,
                Map.class
        );


        Map<String, Object> responseBody = responseEntity.getBody();

        if (responseBody != null) {
            String dailySignal = (String) responseBody.get("daily_signal");
            String weeklySignal = (String) responseBody.get("weekly_signal");
            String monthlySignal = (String) responseBody.get("monthly_signal");

            // Return all three signals in a map
            Map<String, String> signals = new HashMap<>();
            signals.put("daily_signal", dailySignal);
            signals.put("weekly_signal", weeklySignal);
            signals.put("monthly_signal", monthlySignal);

            return signals;
        } else {
            throw new RuntimeException("Failed to retrieve signals from Python API.");
        }

// single signal code
//        if (responseBody != null && responseBody.containsKey("final_signal")) {
//            return responseBody.get("final_signal").toString();
//        } else {
//            throw new RuntimeException("Failed to retrieve a valid signal from the Python API.");
//        }
    }


    public Double predictNextMonth(Long companyId) {

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        List<PriceLogEntity> data = priceLogRepository.findByCompanyIdAndDateBetween(companyId, LocalDate.now().minusMonths(3), LocalDate.now());
        Map<String, Object> requestBody = Map.of("data", mapToRequestData(data));

        HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestBody, headers);
        try {
            // Call the FastAPI endpoint using RestTemplate
            Map<String, Double> response = restTemplate.postForObject(predictionApiUrl, requestEntity, Map.class);
            return response != null ? response.get("predicted_next_month_price") : null;
        } catch (Exception e) {
            // Handle exceptions
            e.printStackTrace();
            return null;
        }
    }

    public static List<Map<String, Object>> mapToRequestData(List<PriceLogEntity> historicalDataEntities) {
        return historicalDataEntities.stream().map(entity -> {
            Map<String, Object> data = new HashMap<>();
            data.put("date", entity.getDate().toString());
            data.put("average_price", entity.getAveragePrice());
            return data;
        }).collect(Collectors.toList());
    }

    public Response analyzeNewsSentiment(Long companyId) throws Exception {
        String apiUrl = "http://127.0.0.1:5000/news_sentiment";

        BusinessEntity business = businessRepository.findById(companyId)
                .orElseThrow(() -> new Exception("Business entity not found"));

        String companyCode = business.getCompanyCode();

        HttpHeaders httpHeaders = new HttpHeaders();
        httpHeaders.setContentType(MediaType.APPLICATION_JSON);

        ResponseEntity<Map> apiResponse = restTemplate.exchange(
                apiUrl + "?company_code=" + companyCode,
                HttpMethod.GET,
                new HttpEntity<>(httpHeaders),
                Map.class
        );

        Map<String, Object> responseContent = apiResponse.getBody();
        if (responseContent == null)
            throw new RuntimeException("The sentiment analysis API returned no data.");


        if (responseContent.containsKey("error")) {
            String errorDetails = (String) responseContent.get("error");
            throw new RuntimeException("Python API reported an error: " + errorDetails);
        }

        Response result = new Response();
        result.score = (Double) responseContent.get("sentiment_score");
        result.recommendation = (String) responseContent.get("recommendation");

        return result;
    }

}
