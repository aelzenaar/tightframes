function products = compute3Products(A)
    n = size(A,2);
    assert(3<=n);
    products = NaN(n^3,1);
    index = 1;
    for it = 1:n
        for jt = 1:n
            for kt = 1:n
                products(index,1) = dot(A(:,it),A(:,jt))*dot(A(:,jt),A(:,kt))*dot(A(:,kt),A(:,it));
                index = index + 1;
            end
        end
    end
    products = sort(products);
end
