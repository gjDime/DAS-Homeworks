package com.example.project1.data;

import com.example.project1.data.pipeline.Pipe;
import com.example.project1.data.pipeline.impl.FilterBusiness;
import com.example.project1.data.pipeline.impl.FilterPriceLog;
import com.example.project1.data.pipeline.impl.FilterReAddPrice;
import com.example.project1.model.BusinessEntity;
import com.example.project1.repository.BusinessRepository;
import com.example.project1.repository.PriceLogRepository;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.text.ParseException;
import java.util.List;

@Component
@RequiredArgsConstructor
public class DataAdder {

    private final BusinessRepository businessRepository;
    private final PriceLogRepository priceLogRepository;

    @PostConstruct
    private void initializeData() throws IOException, ParseException {
        long startTime = System.nanoTime();

        Pipe<List<BusinessEntity>> pipe = new Pipe<>();
        pipe.addFilter(new FilterBusiness(businessRepository));
        pipe.addFilter(new FilterPriceLog(businessRepository, priceLogRepository));
        pipe.addFilter(new FilterReAddPrice(businessRepository, priceLogRepository));
        pipe.runFilter(null);

        long endTime = System.nanoTime();
        long durationInMillis = (endTime - startTime) / 1_000_000;

        long hours = durationInMillis / 3_600_000;
        long minutes = (durationInMillis % 3_600_000) / 60_000;
        long seconds = (durationInMillis % 60_000) / 1_000;

        System.out.printf("Total time for all filters to complete: %02d hours, %02d minutes, %02d seconds%n", hours, minutes, seconds);
    }

}
