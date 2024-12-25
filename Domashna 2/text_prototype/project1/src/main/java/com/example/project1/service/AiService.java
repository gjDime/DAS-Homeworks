package com.example.project1.service;

import com.example.project1.model.PriceLogEntity;
import com.example.project1.repository.PriceLogRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDate;
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

        List<PriceLogEntity> data = priceLogRepository.findByCompanyIdAndDateBetween(companyId, LocalDate.now().minusMonths(1), LocalDate.now());;

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

    /**
     * Sends price logs to the Python server to calculate oscillators.
     *
     * @param priceLogs List of PriceLogEntity objects.
     * @return A map containing oscillator values (e.g., RSI).
     */
    public Map<String, Object> calculateOscillators(List<PriceLogEntity> priceLogs) {
        String url = pythonServerUrl + "/calculate-oscillators/";

        HttpHeaders headers = new HttpHeaders();
        headers.set("Content-Type", "application/json");

        HttpEntity<List<PriceLogEntity>> request = new HttpEntity<>(priceLogs, headers);

        ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.POST, request, Map.class);

        return response.getBody();
    }


    /**
            * Sends price logs to the Python server to calculate moving averages.
     *
             * @param priceLogs List of PriceLogEntity objects.
     * @return A map containing moving average values (e.g., SMA_20, SMA_50).
            */
    public Map<String, Object> calculateMovingAverages(List<PriceLogEntity> priceLogs) {
        String url = pythonServerUrl + "/calculate-moving-averages/";

        HttpHeaders headers = new HttpHeaders();
        headers.set("Content-Type", "application/json");

        HttpEntity<List<PriceLogEntity>> request = new HttpEntity<>(priceLogs, headers);

        ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.POST, request, Map.class);

        return response.getBody();
    }

}
