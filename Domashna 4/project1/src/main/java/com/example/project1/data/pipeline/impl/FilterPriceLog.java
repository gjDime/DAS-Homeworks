package com.example.project1.data.pipeline.impl;

import com.example.project1.data.DataParser;
import com.example.project1.data.pipeline.Filter;
import com.example.project1.model.BusinessEntity;
import com.example.project1.model.PriceLogEntity;
import com.example.project1.repository.BusinessRepository;
import com.example.project1.repository.PriceLogRepository;
import org.jsoup.Connection;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import java.io.IOException;
import java.text.NumberFormat;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;

public class FilterPriceLog implements Filter<List<BusinessEntity>> {

    private final BusinessRepository businessRepository;
    private final PriceLogRepository priceLogRepository;

    private static final String HISTORICAL_DATA_URL = "https://www.mse.mk/mk/stats/symbolhistory/";

    public FilterPriceLog(BusinessRepository businessRepository, PriceLogRepository priceLogRepository) {
        this.businessRepository = businessRepository;
        this.priceLogRepository = priceLogRepository;
    }

    public List<BusinessEntity> execute(List<BusinessEntity> input) throws IOException {
        List<BusinessEntity> companies = new ArrayList<>();
        List<String> toIgnore = Arrays.asList("BLTU", "CBNG", "ELNC", "ENSA", "INHO", "INTP", "KULT", "LAJO", "MPTE", "MZHE",
                "OBPP", "OTEK", "SPOL", "TASK", "TIGA", "TRDB", "VFPM", "ZILUP");
        input = input.stream()
                .filter(i -> !toIgnore.contains(i.getCompanyCode()))
                .toList();
        for (BusinessEntity company : input) {
            if (company.getLastUpdated() == null) {
                System.out.println("KOMPANI PROCESSING NOW: " + company.getCompanyCode());
                for (int i = 1; i <= 10; i++) {
                    int temp = i - 1;
                    LocalDate fromDate = LocalDate.now().minusYears(i);
                    LocalDate toDate = LocalDate.now().minusYears(temp);
                    addHistoricalData(company, fromDate, toDate);
                }
            } else {
                companies.add(company);
            }
        }

        return companies;
    }

    private void addHistoricalData(BusinessEntity company, LocalDate fromDate, LocalDate toDate) throws IOException {
        Connection.Response response = Jsoup.connect(HISTORICAL_DATA_URL + company.getCompanyCode())
                .data("FromDate", fromDate.toString())
                .data("ToDate", toDate.toString())
                .method(Connection.Method.POST)
                .execute();

        Document document = response.parse();

        Element table = document.select("table#resultsTable").first();

        if (table != null) {
            Elements rows = table.select("tbody tr");

            for (Element row : rows) {
                Elements columns = row.select("td");

                if (columns.size() > 0) {
                    LocalDate date = DataParser.parseDate(columns.get(0).text(), "d.M.yyyy");

                    if (priceLogRepository.findByDateAndCompany(date, company).isEmpty()) {


                        NumberFormat format = NumberFormat.getInstance(Locale.GERMANY);

                        Double lastTransactionPrice = DataParser.parseDouble(columns.get(1).text(), format);
                        Double maxPrice = DataParser.parseDouble(columns.get(2).text(), format);
                        Double minPrice = DataParser.parseDouble(columns.get(3).text(), format);
                        Double averagePrice = DataParser.parseDouble(columns.get(4).text(), format);
                        Double percentageChange = DataParser.parseDouble(columns.get(5).text(), format);
                        Integer quantity = DataParser.parseInteger(columns.get(6).text(), format);
                        Integer turnoverBest = DataParser.parseInteger(columns.get(7).text(), format);
                        Integer totalTurnover = DataParser.parseInteger(columns.get(8).text(), format);

                        if (maxPrice != null) {

                            if (company.getLastUpdated() == null || company.getLastUpdated().isBefore(date)) {
                                company.setLastUpdated(date);
                            }

                            PriceLogEntity priceLogEntity = new PriceLogEntity(
                                    date, lastTransactionPrice, maxPrice, minPrice, averagePrice, percentageChange,
                                    quantity, turnoverBest, totalTurnover);
                            priceLogEntity.setCompany(company);
                            priceLogRepository.save(priceLogEntity);
                            company.getHistoricalData().add(priceLogEntity);
                        }
                    }
                }
            }
        }

        businessRepository.save(company);
    }

}
