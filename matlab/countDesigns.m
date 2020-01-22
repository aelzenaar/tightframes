d = 3;
n = 27;
t = 3;
k = 100; % Iterations
accuracy = 4;

errorComputer = ComplexDesignPotential(d,n,t);

tripleProducts = NaN(n^3,k);

for it = 1:k
    fprintf(1,"[%04d/%d] generating design... ",it,k);
    [result, ~, ~] = iterateOnDesignMO(NaN(d,n), 1e4, errorComputer);
    fprintf(1,"computing triple products... ");
    tripleProducts(:,it) = round(compute3Products(result).',accuracy);
    fprintf(1,"done.\n");
end

[tripleProductsUnique,~,ic] = uniquetol(abs(tripleProducts).', accuracy, 'ByRows', true);
tripleProductsUnique = tripleProductsUnique.';
tripleProducts_ratios = accumarray(ic,1)./k;

fprintf(1,"\nFound total of %d/%d unique triple-products to %d figures.\n",size(tripleProductsUnique,2),k,accuracy);
fprintf(1,"These were distributed as follows: ");
for it = 1:size(tripleProducts_ratios)
    fprintf(1, "%.02f%%", tripleProducts_ratios(it)*100);
end
fprintf(1,"\n");

