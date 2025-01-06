package com.example.project1.data.pipeline.impl;

import com.example.project1.data.FilterUtils;
import com.example.project1.data.pipeline.Filter;
import com.example.project1.model.BusinessEntity;
import com.example.project1.repository.BusinessRepository;
import com.example.project1.repository.PriceLogRepository;

import java.io.IOException;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class FilterPriceLog implements Filter<List<BusinessEntity>> {
    private final FilterUtils filterUtils;

    public FilterPriceLog(BusinessRepository businessRepository, PriceLogRepository priceLogRepository) {
        filterUtils = new FilterUtils(businessRepository, priceLogRepository);
    }

    private List<BusinessEntity> filterInput(List<BusinessEntity> input) {
        List<String> toIgnoreIssuers = Arrays.asList("BLTU", "CBNG", "ELNC", "ENSA", "INHO", "INTP", "KULT", "LAJO", "MPTE", "MZHE",
                "OBPP", "OTEK", "SPOL", "TASK", "TIGA", "TRDB", "VFPM", "ZILUP");

        //filter input issuers
        return input.stream()
                .filter(i -> !toIgnoreIssuers.contains(i.getCompanyCode()))
                .toList();
    }

    public List<BusinessEntity> execute(List<BusinessEntity> input) throws IOException {
        System.out.println("filter2 started");
        input = filterInput(input);


        List<BusinessEntity> companies = new ArrayList<>();
        for (BusinessEntity company : input) {
            if (company.getLastUpdated() == null) {//fetch last 10 years
                System.out.println("COMPANY PROCESSING " + company.getCompanyCode());
                for (int i = 1; i <= 10; i++) {
                    LocalDate fromDate = LocalDate.now().minusYears(i);
                    LocalDate toDate = LocalDate.now().minusYears(i - 1);
                    filterUtils.addHistoricalData(company, fromDate, toDate);
                }
            } else {
                companies.add(company);
            }
        }

        return companies;
    }
}
