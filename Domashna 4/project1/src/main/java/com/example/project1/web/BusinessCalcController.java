package com.example.project1.web;

import com.example.project1.model.dto.Response;
import com.example.project1.service.BusinessCalcService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class BusinessCalcController {

    private final BusinessCalcService businessCalcService;

    @PostMapping("/tehnicals")
    public ResponseEntity<Map<String, String>> technicals(@RequestParam(name = "companyId") Long companyId) {//technicalAnalysis
        System.out.println("/api/tehnicals");
        Map<String, String> signals = businessCalcService.technicalAnalysis(companyId);
        System.out.println(signals.values());
        return ResponseEntity.ok(signals);
    }
    @GetMapping("/news")
    public ResponseEntity<Response> processNews(@RequestParam(name = "companyId") Long companyId) throws Exception {
        Response response = businessCalcService.analyzeNewsSentiment(companyId);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/predict")
    public ResponseEntity<Double> predictPrice(@RequestParam(name = "companyId") Long companyId) {//lstm
        double predictedPrice = businessCalcService.predictNextMonth(companyId);
        return ResponseEntity.ok(predictedPrice);
    }
}
