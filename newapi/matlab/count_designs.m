% Count the number of designs with given parameters, up to unitary
% projective equivalence.
%
% Parameters: dp       - instance of DesignParameters object.
%             k        - number of designs to generate for the partioning.
%             accuracy - number of decimal places to compare triple
%                        products to.
%
% Output: tripleProductRatios - a list of ratios, adding to 1, that give
%                               the relative equivalence class sizes.
function tripleProductRatios = count_designs(dp, k, accuracy)
    [d,n,t] = dp.getParameters();
    tripleProducts = NaN(n^3,k);

    for it = 1:k
        fprintf(1,"[%04d/%d] generating design... ",it,k);
        [result, ~, ~] = produce_design(dp,[]);
        fprintf(1,"computing triple products... ");
        tripleProducts(:,it) = round(compute_triple_products(result).',accuracy);
        fprintf(1,"done.\n");
    end

    disp(tripleProducts);
    [tripleProductsUnique,~,ic] = uniquetol(abs(tripleProducts).', 10^-(accuracy), 'ByRows', true);
    tripleProductsUnique = tripleProductsUnique.';
    disp(tripleProductsUnique.');
    tripleProductRatios = accumarray(ic,1)./k;

    fprintf(1,"\nFound total of %d/%d unique triple-products to %d figures.\n",size(tripleProductsUnique,2),k,accuracy);
    fprintf(1,"These were distributed as follows: ");
    for it = 1:size(tripleProductRatios)
        fprintf(1, "%.02f%% ", tripleProductRatios(it)*100);
    end
    fprintf(1,"\n");
end
