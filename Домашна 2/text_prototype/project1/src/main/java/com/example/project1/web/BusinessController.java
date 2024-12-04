package com.example.project1.web;

import com.example.project1.model.BusinessEntity;
import com.example.project1.model.PriceLogEntity;
import com.example.project1.service.BusinessService;
import com.example.project1.service.AiService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Controller
@RequiredArgsConstructor
public class BusinessController {

    private final BusinessService businessService;
    private final AiService AiService;

    @GetMapping("/")
    public String getIndexPage(Model model) {
        model.addAttribute("companies", businessService.findAll());
        return "index";
    }

    @GetMapping("/today")
    public String getTodayCompanyPage(Model model) {
        model.addAttribute("prices", businessService.findAllToday());
        return "today";
    }

    @GetMapping("/company")
    public String getCompanyPage(@RequestParam(name = "companyId") Long companyId, Model model) throws Exception {
        List<Map<String, Object>> companyData = new ArrayList<>();
        BusinessEntity company = businessService.findById(companyId);

        Map<String, Object> data = new HashMap<>();
        data.put("companyCode", company.getCompanyCode());
        data.put("lastUpdated", company.getLastUpdated());

        List<LocalDate> dates = new ArrayList<>();
        List<Double> prices = new ArrayList<>();

        for (PriceLogEntity historicalData : company.getHistoricalData()) {
            dates.add(historicalData.getDate());
            prices.add(historicalData.getLastTransactionPrice());
        }

        data.put("dates", dates);
        data.put("prices", prices);
        data.put("id", company.getId());
        companyData.add(data);

        model.addAttribute("companyData", companyData);
        return "company";
    }

}
