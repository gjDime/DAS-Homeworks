package com.example.project1.service;

import com.example.project1.model.PriceLogEntity;
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

    private final String predictionApiUrl = "http://127.0.0.1:8000/predict-next-month-price/";
    private final String tehnicalsUrl = "http://127.0.0.1:5000/generate_signal";

    public BusinessCalcService(PriceLogRepository priceLogRepository, BusinessRepository businessRepository) {
        this.priceLogRepository = priceLogRepository;
        this.businessRepository = businessRepository;
    }

    public String technicalAnalysis(Long companyId) {
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
        if (responseBody != null && responseBody.containsKey("final_signal")) {
            return responseBody.get("final_signal").toString();
        } else {
            throw new RuntimeException("Failed to retrieve a valid signal from the Python API.");
        }
    }


    public Double predictNextMonth(Long companyId) {

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        List<PriceLogEntity> data = priceLogRepository.findByCompanyIdAndDateBetween(companyId, LocalDate.now().minusMonths(1), LocalDate.now());
        Map<String, Object> requestBody = Map.of("data", mapToRequestData(data));

        HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestBody, headers);
        Map<String, Double> response = restTemplate.postForObject(predictionApiUrl, requestEntity, Map.class);

        return response != null ? response.get("predicted_next_month_price") : null;
    }

    public static List<Map<String, Object>> mapToRequestData(List<PriceLogEntity> historicalDataEntities) {
        return historicalDataEntities.stream().map(entity -> {
            Map<String, Object> data = new HashMap<>();
            data.put("date", entity.getDate().toString());
            data.put("average_price", entity.getAveragePrice());
            return data;
        }).collect(Collectors.toList());
    }
}
