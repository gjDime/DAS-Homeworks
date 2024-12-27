package com.example.project1.web;

import com.example.project1.service.BusinessCalcService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class BusinessCalcController {

    private final BusinessCalcService BusinessCalcService;


    @PostMapping("/tehnicals")
    public ResponseEntity<String> technicals(@RequestParam(name = "companyId") Long companyId) {//technicalAnalysis
        String response = BusinessCalcService.technicalAnalysis(companyId);
        return ResponseEntity.ok(response);
    }

    //TODO
    @PostMapping("/predict")
    public ResponseEntity<Double> predictPrice(@RequestParam(name = "companyId") Long companyId) {//lstm
        double predictedPrice = BusinessCalcService.predictNextMonth(companyId);
        return ResponseEntity.ok(predictedPrice);
    }

}
