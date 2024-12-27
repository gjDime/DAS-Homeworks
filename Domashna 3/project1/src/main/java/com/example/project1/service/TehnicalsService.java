package com.example.project1.service;

import com.example.project1.model.PriceLogEntity;
import com.example.project1.repository.PriceLogRepository;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class TehnicalsService {
    private final PriceLogRepository priceLogRepository;
    private final String apiUrl = "http://127.0.0.1:8000/";
    private final RestTemplate restTemplate = new RestTemplate();

    public TehnicalsService(PriceLogRepository priceLogRepository) {
        this.priceLogRepository = priceLogRepository;
    }

    private Map<String, Object> mapEntityToRequest(List<PriceLogEntity> historicalDataEntities) {
        // Define the columns
        List<String> columns = List.of(
                "date",
                "last_transaction_price",
                "max_price",
                "min_price",
                "average_price",
                "percentage_change",
                "quantity",
                "turnover_best",
                "total_turnover"
        );

        // Map the entities to rows of data
        List<List<Object>> data = historicalDataEntities.stream()
                .map(entity -> List.of(
                        entity.getDate().toString(),
                        entity.getLastTransactionPrice(),
                        entity.getMaxPrice(),
                        entity.getMinPrice(),
                        entity.getAveragePrice(),
                        entity.getPercentageChange(),
                        entity.getQuantity(),
                        entity.getTurnoverBest(),
                        (Object) entity.getTotalTurnover()
                ))
                .toList();

        // Combine columns and data into the required structure
        return Map.of(
                "columns", columns,
                "data", data
        );
    }
    public Map<String, Object> calcOscillatorsAllTimeframes(Long companyId) {
        String url = apiUrl + "calculate-timeframes";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        List<PriceLogEntity> data = priceLogRepository.findByCompanyIdAndDateBetween(
                companyId,
                LocalDate.now().minusMonths(1),
                LocalDate.now()
        );

        //serialize data
        Map<String, Object> requestBody = mapEntityToRequest(data);
        HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestBody, headers);

        try {
            ResponseEntity<Map> responseEntity = restTemplate.postForEntity(url, requestEntity, Map.class);

            if (responseEntity.getStatusCode() == HttpStatus.OK) {
                return responseEntity.getBody();
            } else {
                throw new RuntimeException("Unexpected response status: " + responseEntity.getStatusCode());
            }
        } catch (RestClientException e) {
            throw new RuntimeException("Failed to call external API: " + e.getMessage(), e);
        }
    }


}
