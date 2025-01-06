package com.example.project1.data.pipeline.impl;

import com.example.project1.data.FilterUtils;
import com.example.project1.data.pipeline.Filter;
import com.example.project1.model.BusinessEntity;
import com.example.project1.repository.BusinessRepository;
import com.example.project1.repository.PriceLogRepository;

import java.io.IOException;
import java.time.LocalDate;
import java.util.List;

public class FilterReAddPrice implements Filter<List<BusinessEntity>> {
    private final FilterUtils filterUtils;

    public FilterReAddPrice(BusinessRepository businessRepository, PriceLogRepository priceLogRepository) {
        filterUtils = new FilterUtils(businessRepository, priceLogRepository);
    }

    public List<BusinessEntity> execute(List<BusinessEntity> input) throws IOException {
        System.out.println("filter3 started");
        for (BusinessEntity company : input) {
            LocalDate fromDate = company.getLastUpdated();
            LocalDate toDate = LocalDate.now();
            filterUtils.addHistoricalData(company, fromDate, toDate);
        }

        return null;
    }
}
