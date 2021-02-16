t = 2;
d = 3;
n = 6;
k = 100; % Iterations
accuracy = 25;
threshold = 1e-9;

errorComputer = RealDesignPotential(d,n,t,'weighted');

tripleProducts = NaN(n^3,k);

it = 1;
while it <= k
    fprintf(1,"[%04d/%d] generating design... ",it,k);
    [result, cost, ~] = iterateOnDesignMO(NaN(d,n), 1e4, errorComputer);
    if(cost(end) < threshold)
        fprintf(1,"computing triple products... ");
        tripleProducts(:,it) = round(compute3Products(result).',accuracy);
        fprintf(1,"done.\n");
        it = it + 1;
    else
        fprintf(1,"not found to tolerance\n");
    end
end

[tripleProductsUnique,~,ic] = uniquetol(abs(tripleProducts).', 1/9, 'ByRows', true);
tripleProductsUnique = tripleProductsUnique.';
tripleProducts_ratios = accumarray(ic,1)./k;

fprintf(1,"\nFound total of %d/%d unique triple-products to %d figures.\n",size(tripleProductsUnique,2),k,accuracy);
fprintf(1,"These were distributed as follows: ");
for it = 1:size(tripleProducts_ratios)
    fprintf(1, "%.02f%% ", tripleProducts_ratios(it)*100);
end
fprintf(1,"\n");

