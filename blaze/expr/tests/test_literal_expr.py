import numpy as np
import pandas as pd
import pytest
import re


from datashape import dshape

from blaze import discover, transform
from blaze.expr import data, literal
from blaze.utils import normalize


tdata = (('Alice', 100),
         ('Bob', 200))

L = [[1, 'Alice',   100],
     [2, 'Bob',    -200],
     [3, 'Charlie', 300],
     [4, 'Denis',   400],
     [5, 'Edith',  -500]]

l = literal(tdata)
nl = literal(tdata, name='amounts')
t = data(tdata, fields=['name', 'amount'])


def test_discover_on_data():
    assert discover(t) == dshape("2 * {name: string, amount: int64}")


def test_discover_on_literal():
    assert discover(l) == dshape("2 * (string, int64)")


def test_table_raises_on_inconsistent_inputs():
    with pytest.raises(ValueError) as excinfo:
        data(tdata, schema='{name: string, amount: float32}',
             dshape=dshape("{name: string, amount: float32}"))
    assert "specify one of schema= or dshape= keyword" in str(excinfo.value)


def test_resources():
    assert t._resources() == {t: t.data}


def test_literal_repr():
    assert "(('Alice', 100), ('Bob', 200))" == repr(l)


def test_literal_name_repr():
    assert "amounts" == repr(nl)


def test_data_repr():
    def replace_name(s):

        # Account for autogenerated name.
        return re.sub(r"name='(.*)'", "name='_0'", s)
    expected = "<'tuple' data; _name='.+', dshape='2 * {name: string, amount: int64}'>"  # noqa
    assert replace_name(expected) == replace_name(repr(t))


def test_str_does_not_repr():
    # see GH issue #1240.
    d = data(
        [('aa', 1), ('b', 2)],
        name="ZZZ",
        dshape='2 * {a: string, b: int64}',
    )
    expr = transform(d, c=d.a.str.len() + d.b)
    assert (
        normalize(str(expr)) ==
        normalize("""
            Merge(
                args=(ZZZ, label(len(_child=ZZZ.a) + ZZZ.b, 'c')),
                _varargsexpr=VarArgsExpr(
                    _inputs=(ZZZ, label(len(_child=ZZZ.a) + ZZZ.b, 'c'))
                ),
                _shape=(2,)
            )
        """)
    )


def test_isidentical_regr():
    # regression test for #1387
    tdata = np.array([(np.nan,), (np.nan,)], dtype=[('a', 'float64')])
    ds = data(tdata)
    assert ds.a.isidentical(ds.a)