package com.example.project1.web;

import com.example.project1.service.BusinessCalcService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

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

    //TODO
    @PostMapping("/predict")
    public ResponseEntity<Double> predictPrice(@RequestParam(name = "companyId") Long companyId) {//lstm
        double predictedPrice = businessCalcService.predictNextMonth(companyId);
        return ResponseEntity.ok(predictedPrice);
    }

}
