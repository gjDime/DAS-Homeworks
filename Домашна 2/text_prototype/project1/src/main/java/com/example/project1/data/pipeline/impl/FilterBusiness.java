package com.example.project1.data.pipeline.impl;

import com.example.project1.data.pipeline.Filter;
import com.example.project1.model.BusinessEntity;
import com.example.project1.repository.BusinessRepository;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import java.io.IOException;
import java.util.List;

public class FilterBusiness implements Filter<List<BusinessEntity>> {

    private final BusinessRepository businessRepository;

    public FilterBusiness(BusinessRepository businessRepository) {
        this.businessRepository = businessRepository;
    }

    private static final String STOCK_MARKET_URL = "https://www.mse.mk/mk/stats/symbolhistory/kmb";

    @Override
    public List<BusinessEntity> execute(List<BusinessEntity> input) throws IOException {
        Document document = Jsoup.connect(STOCK_MARKET_URL).get();
        Element selectMenu = document.select("select#Code").first();

        if (selectMenu != null) {
            Elements options = selectMenu.select("option");
            for (Element option : options) {
                String code = option.attr("value");
                if (!code.isEmpty() && code.matches("^[a-zA-Z]+$")) {
                    if (businessRepository.findByCompanyCode(code).isEmpty()) {
                        businessRepository.save(new BusinessEntity(code));
                    }
                }
            }
        }

        return businessRepository.findAll();
    }
}
